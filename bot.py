import json
import os
import random
import re

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))

COUNTER_FILE = "counter.json"
TRIGGER_RE = re.compile(r"impeach\w*\s+(\w+\s+){0,3}again", re.IGNORECASE)

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
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    suffixes = ["th", "st", "nd", "rd"]
    return f"{n}{suffixes[min(n % 10, 3)] if n % 10 <= 3 else 'th'}"


def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE) as f:
        return json.load(f).get("count", 0)


def save_counter(n):
    tmp = COUNTER_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"count": n}, f)
    os.replace(tmp, COUNTER_FILE)


def make_response(n):
    template = random.choice(RESPONSES)
    return template.format(n=n, ord=ordinal(n))


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if TRIGGER_RE.search(message.content):
        count = load_counter() + 1
        save_counter(count)
        await message.channel.send(make_response(count))


@tree.command(name="impeach", description="Impeach him again!")
async def impeach(interaction: discord.Interaction):
    count = load_counter() + 1
    save_counter(count)
    await interaction.response.send_message(make_response(count))


@tree.command(name="impeachments", description="Check the total impeachment count")
async def impeachments(interaction: discord.Interaction):
    count = load_counter()
    await interaction.response.send_message(COUNT_RESPONSE.format(n=count))


@tree.command(name="setcount", description="(Admin) Set the impeachment counter")
@app_commands.describe(value="The new counter value")
async def setcount(interaction: discord.Interaction, value: int):
    if interaction.user.id != ADMIN_USER_ID:
        await interaction.response.send_message("You don't have permission to do that.", ephemeral=True)
        return
    save_counter(value)
    await interaction.response.send_message(f"Counter set to {value}.", ephemeral=True)


client.run(DISCORD_TOKEN)
