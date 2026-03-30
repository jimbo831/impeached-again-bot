# Impeached Again Bot

A Discord bot for tracking a running "impeached again" joke count. See `bot-spec.md` for full behavioral spec including trigger mechanism, response strings, and command details.

## Stack
- Python with discord.py
- JSON file for persistent counter storage
- Hosted on a Mac Mini home server

## Philosophy
Prefer simple and minimal solutions. Avoid overengineering.

## Project Structure
- `bot.py` — main bot file
- `counter.json` — persistent counter storage (auto-created if missing, not committed)
- `.env` — secrets (not committed)

## Environment Variables
Defined in `.env`:
- `DISCORD_TOKEN` — the bot token
- `ADMIN_USER_ID` — Discord user ID for admin commands

## Git Commits
Do not mention Claude, AI, or any AI assistant in commit messages or co-author lines.

## Running the Bot
```bash
source venv/bin/activate
python bot.py
```
