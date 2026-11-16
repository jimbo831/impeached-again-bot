# Impeached Again Bot

A Discord bot for tracking a running "impeached again" joke count. See `bot-spec.md` for full behavioral spec including trigger mechanism, response strings, and command details.

## Stack
- Python with discord.py
- JSON file for persistent counter storage
- Hosted on an Oracle Cloud VM as a systemd service (`impeached-again-bot`), monitored by Uptime Kuma on the same VM

## Philosophy
Prefer simple and minimal solutions. Avoid overengineering.

## Project Structure
- `bot.py` — main bot file
- `test_bot.py` — unit tests (stdlib `unittest`)
- `.github/workflows/deploy.yml` — runs tests on every push; deploys to the VM on pushes to `main` (or manually for any branch)
- `counter.json` — persistent counter storage (auto-created if missing, not committed). The live copy exists only on the VM and is never touched by deploys.
- `.env` — secrets (not committed). On the VM it is rewritten from GitHub secrets on every deploy.

## Environment Variables
Defined in `.env`:
- `DISCORD_TOKEN` — the bot token
- `ADMIN_USER_ID` — Discord user ID for admin commands
- `UPTIME_KUMA_PUSH_URL` — optional Uptime Kuma push monitor URL (without the `?` query); status reporting is skipped if unset

## Testing
Always run the tests (`python -m unittest`) after making changes. Consider whether a change needs new or updated tests in `test_bot.py`, but keep tests straightforward and short.

## Git Commits
Do not mention Claude, AI, or any AI assistant in commit messages or co-author lines.

## Running the Bot
```bash
source .venv/bin/activate
python bot.py
```
