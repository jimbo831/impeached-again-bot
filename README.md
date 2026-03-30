# Impeached Again Bot

A Discord bot that tracks a running "impeached again" count, responding with satirical messages whenever impeachment is mentioned.

## Features

- **Keyword detection** — triggers on any message matching `impeach* ... again` (case-insensitive)
- **Slash commands** — `/impeach` and `/impeachments`
- **Persistent counter** — survives restarts via a local JSON file
- **13 randomized responses** — drawn from a pool of political satire

## Commands

| Command | Description |
|---|---|
| `/impeach` | Increments the counter and responds with a random message |
| `/impeachments` | Displays the current count without incrementing |

## Setup

### Prerequisites

- Python 3.10+
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))

### Install

```bash
git clone <repo-url>
cd impeached-again-bot
python -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv
```

### Configure

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_discord_user_id_here
```

`ADMIN_USER_ID` is your personal Discord user ID (enables admin commands like resetting the counter).

### Run

```bash
source .venv/bin/activate
python bot.py
```

## Hosting

Designed to run on a Mac Mini home server. Use `launchd` or a simple shell script to keep it running.