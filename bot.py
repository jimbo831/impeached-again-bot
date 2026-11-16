import asyncio
import datetime
import json
import math
import os
import random
import re
import string
import urllib.parse
import urllib.request

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from responses import COUNT_RESPONSE, RESPONSES

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
UPTIME_KUMA_PUSH_URL = os.getenv("UPTIME_KUMA_PUSH_URL")
EIA_API_KEY = os.getenv("EIA_API_KEY")


def push_status(status, msg, ping=""):
    """Report status to the Uptime Kuma push monitor, if one is configured."""
    if not UPTIME_KUMA_PUSH_URL:
        return
    query = urllib.parse.urlencode({"status": status, "msg": msg[:200], "ping": ping})
    try:
        urllib.request.urlopen(f"{UPTIME_KUMA_PUSH_URL}?{query}", timeout=10).close()
    except Exception as e:
        print(f"Uptime Kuma push failed: {e}", flush=True)


COUNTER_FILE = "counter.json"
TRIGGER_RE = re.compile(r"\bimpeach\w*\W+(?:\w+\W+){0,3}again\b", re.IGNORECASE)


def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def load_data():
    if not os.path.exists(COUNTER_FILE):
        return {"guilds": {}}
    with open(COUNTER_FILE) as f:
        return json.load(f)


def save_data(data):
    tmp = COUNTER_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, COUNTER_FILE)


def get_count(data, guild_id):
    return data["guilds"].get(str(guild_id), {}).get("count", 0)


def set_count(data, guild_id, guild_name, n):
    data["guilds"][str(guild_id)] = {"name": guild_name, "count": n}


def increment_count(guild):
    # No awaits in here: the bot handles one event at a time between awaits,
    # so this load-modify-save can't interleave with another trigger.
    data = load_data()
    count = get_count(data, guild.id) + 1
    set_count(data, guild.id, guild.name, count)
    save_data(data)
    return count


def fetch_json(url):
    # Some sites block Python's default User-Agent; send a generic one instead
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch_approval():
    # ElectionsUSA polling average (CC BY 4.0)
    data = fetch_json("https://electionsusa.org/api/approval-trump-2.json")
    return round(data["average"]["Approve"])


def fetch_gas_price():
    # EIA weekly U.S. average retail price, regular gasoline
    if not EIA_API_KEY:
        raise RuntimeError("EIA_API_KEY not set")
    query = urllib.parse.urlencode({
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[series][]": "EMM_EPMR_PTE_NUS_DPG",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    })
    data = fetch_json(f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?{query}")
    return f"{float(data['response']['data'][0]['value']):.2f}"


LIVE_FETCHERS = {"approval": fetch_approval, "gas_price": fetch_gas_price}
live_values = {}  # last successful value for each fetcher; kept if a later fetch fails
live_failures = {}  # name -> (consecutive failures, last error)


def live_data_problem():
    """Describe live lookups that have failed 3 times in a row (about 2 hours), or return None."""
    failing = [f"{name}: {error}" for name, (count, error) in live_failures.items() if count >= 3]
    if failing:
        return f"Live data lookup failing ({'; '.join(failing)}). Bot is otherwise running."
    return None


def trump_age(today=None):
    today = today or datetime.date.today()
    return today.year - 1946 - ((today.month, today.day) < (6, 14))


# Shuffle bag: every response is used once before any repeats. In memory only,
# so a restart starts a fresh shuffle.
_bag = []
_last = None


def next_template():
    global _last
    if not _bag:
        _bag.extend(random.sample(RESPONSES, len(RESPONSES)))
        if _bag[-1] == _last:  # don't repeat across the reshuffle
            _bag[0], _bag[-1] = _bag[-1], _bag[0]
    _last = _bag.pop()
    return _last


def make_response(count):
    values = {"count": count, "ordinal": ordinal(count), "age": trump_age(), **live_values}
    for _ in range(len(RESPONSES)):
        template = next_template()
        fields = {name for _, name, _, _ in string.Formatter().parse(template) if name}
        if fields <= values.keys():  # skip responses whose live value isn't available
            return template.format(**values)
    return f"Impeachment #{count}."


class ImpeachBot(discord.Client):
    async def setup_hook(self):
        # Runs once at startup, unlike on_ready which also fires on reconnects
        await tree.sync()
        heartbeat.start()
        refresh_live_values.start()


intents = discord.Intents.default()
intents.message_content = True
client = ImpeachBot(intents=intents)
tree = app_commands.CommandTree(client)


@tasks.loop(minutes=5)
async def heartbeat():
    if not math.isfinite(client.latency):
        return  # disconnected from Discord; skip so Kuma notices if it lasts
    try:
        load_data()
    except Exception as e:
        await asyncio.to_thread(push_status, "down", f"Can't read {COUNTER_FILE}: {e}")
        return
    problem = live_data_problem()
    if problem:
        await asyncio.to_thread(push_status, "down", problem)
        return
    await asyncio.to_thread(push_status, "up", "OK", round(client.latency * 1000))


@tasks.loop(hours=1)
async def refresh_live_values():
    for name, fetch in LIVE_FETCHERS.items():
        try:
            live_values[name] = await asyncio.to_thread(fetch)
            live_failures.pop(name, None)
        except Exception as e:
            count = live_failures.get(name, (0, None))[0] + 1
            live_failures[name] = (count, str(e))
            print(f"Live value {name} failed ({count} in a row): {e}", flush=True)


@heartbeat.before_loop
async def before_heartbeat():
    await client.wait_until_ready()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}", flush=True)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if TRIGGER_RE.search(message.content):
        if message.guild is None:
            return  # ignore DMs
        if not message.channel.permissions_for(message.guild.me).send_messages:
            return  # can't reply here, so don't count it
        count = increment_count(message.guild)
        await message.channel.send(make_response(count))


@tree.command(name="impeach", description="Impeach him again!")
@app_commands.guild_only()
async def impeach(interaction: discord.Interaction):
    count = increment_count(interaction.guild)
    await interaction.response.send_message(make_response(count))


@tree.command(name="impeachments", description="Check the total impeachment count")
@app_commands.guild_only()
async def impeachments(interaction: discord.Interaction):
    data = load_data()
    count = get_count(data, interaction.guild_id)
    await interaction.response.send_message(COUNT_RESPONSE.format(count=count))


@tree.command(name="setcount", description="(Admin) Set the impeachment counter")
@app_commands.guild_only()
@app_commands.describe(value="The new counter value")
async def setcount(interaction: discord.Interaction, value: app_commands.Range[int, 0]):
    if str(interaction.user.id) != ADMIN_USER_ID:
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    data = load_data()
    set_count(data, interaction.guild_id, interaction.guild.name, value)
    save_data(data)
    await interaction.response.send_message(f"Counter set to {value}.", ephemeral=True)


if __name__ == "__main__":
    if not DISCORD_TOKEN or not ADMIN_USER_ID.isdigit():
        error = "DISCORD_TOKEN and a numeric ADMIN_USER_ID must be set in .env"
        push_status("down", error)
        raise SystemExit(error)
    try:
        client.run(DISCORD_TOKEN)
    except Exception as e:
        push_status("down", f"Bot stopped: {e}")
        raise
