# Impeached Again Bot

A Discord bot that tracks a running "impeached again" count, responding with satirical messages whenever impeachment is mentioned.

## Features

- **Keyword detection** — triggers on any message matching `impeach* ... again` (case-insensitive)
- **Slash commands** — `/impeach`, `/impeachments`, and admin-only `/setcount`
- **Per-server counters** — each Discord server tracks its own count, persisted in a local JSON file
- **13 randomized responses** — drawn from a pool of political satire
- **Uptime monitoring** — optional status reporting to an Uptime Kuma push monitor

## Commands

| Command | Description |
|---|---|
| `/impeach` | Increments the counter and responds with a random message |
| `/impeachments` | Displays the current count without incrementing |
| `/setcount` | (Admin only) Sets the counter to a given value |

## Setup

### Prerequisites

- Python 3.10+ (production runs 3.14)
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))

### Install

```bash
git clone <repo-url>
cd impeached-again-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_discord_user_id_here
UPTIME_KUMA_PUSH_URL=http://localhost:3001/api/push/your_token
```

`ADMIN_USER_ID` is your personal Discord user ID (enables `/setcount`). `UPTIME_KUMA_PUSH_URL` is optional; leave it out to skip status reporting.

### Run

```bash
source .venv/bin/activate
python bot.py
```

### Test

```bash
python -m unittest
```

## Deployment

The bot runs on an Oracle Cloud VM as a systemd service, deployed by GitHub Actions (`.github/workflows/deploy.yml`):

- Every push runs the tests.
- Pushes to `main` then deploy: `bot.py` and `requirements.txt` are copied to the VM, `.env` is written from GitHub secrets, dependencies are installed, and the service is restarted. The deploy fails if the bot doesn't log in within 30 seconds.
- Any branch can be deployed manually from the Actions tab by running the workflow with "Deploy this branch" checked.

Required GitHub secrets: `VM_HOST`, `VM_SSH_KEY`, `DISCORD_TOKEN`, `ADMIN_USER_ID`, and optionally `UPTIME_KUMA_PUSH_URL`.

The live `counter.json` exists only on the VM and is not touched by deploys.
