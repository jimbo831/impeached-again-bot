import asyncio
import json
import math
import os
import random
import re
import urllib.parse
import urllib.request

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "")
UPTIME_KUMA_PUSH_URL = os.getenv("UPTIME_KUMA_PUSH_URL")


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

# {n} = raw number, {ord} = properly formatted ordinal (e.g. "1st", "2nd")
RESPONSES = [
    "Trump has been impeached again! That's {n} times and counting.",
    "{n} impeachments and counting. Possibly the most in history. Nobody knows.",
    "Another day, another impeachment. Count: {n}",
    "Madam Speaker, we got him. Again. (#{n})",
    "Article I, Article II, Article {n}. Impeached. Again.",
    "WITCH HUNT! HOAX! ...Impeachment #{n}.",
    "You're ~~fired~~ impeached. Again. (#{n})",
    "Many people are saying this is the greatest impeachment. Maybe ever. The {ord}.",
    "This is it. This is definitely the one. He can't survive this. ...Impeachment #{n}.",
    "Please, please. It's too much impeaching. We can't take it anymore, it's too much.\nNo it isn't. We have to keep impeaching. We have to impeach {n} more times!",
    "It was a perfect impeachment. The most perfect. READ THE TRANSCRIPT. (#{n})",
    "A big, strong man came up to me — tough guy, you wouldn't believe it — tears in his eyes. He said, 'Sir, this is the {ord} impeachment.' I said, 'I know. Aren't they beautiful?'",
    "Just got word that the Radical Left has done it AGAIN. That's {n} Total Impeachments, each one more PERFECT and BEAUTIFUL than the last. SAD!!!",
]

COUNT_RESPONSE = "THE FAKE NEWS MEDIA won't tell you this, but the Total Impeachment Count is now {n}. WITCH HUNT!!! Thank you for your attention to this matter!"


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


def make_response(n):
    template = random.choice(RESPONSES)
    return template.format(n=n, ord=ordinal(n))


class ImpeachBot(discord.Client):
    async def setup_hook(self):
        # Runs once at startup, unlike on_ready which also fires on reconnects
        await tree.sync()
        heartbeat.start()


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
    await asyncio.to_thread(push_status, "up", "OK", round(client.latency * 1000))


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
    await interaction.response.send_message(COUNT_RESPONSE.format(n=count))


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
