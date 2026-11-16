# Impeached Again Bot

A Discord bot that tracks a running "impeached again" count, responding with satirical messages whenever impeachment is mentioned.

## Features

- **Keyword detection** — triggers on any message matching `impeach* ... again` (case-insensitive)
- **Slash commands** — `/impeach`, `/impeachments`, and admin-only `/setcount`
- **Per-server counters** — each Discord server tracks its own count, persisted in a local JSON file
- **Satirical responses** — a large pool in `responses.py`, shuffled so none repeats until all have been used
- **Live values** — some responses include Trump's current approval rating ([ElectionsUSA](https://electionsusa.org/approval/trump/) average) and the national average gas price ([EIA](https://www.eia.gov/petroleum/gasdiesel/)), refreshed hourly
- **Uptime monitoring** — optional status reporting to an Uptime Kuma push monitor, including live-data lookup failures

## Commands

| Command | Description |
|---|---|
| `/impeach` | Increments the counter and responds with a random message |
| `/impeachments` | Displays the current count without incrementing |
| `/setcount` | (Admin only) Sets the counter to a given value |

## Setup

### Prerequisites

- Python 3.10+ (production runs 3.14)
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications)), with **Message Content Intent** enabled under Bot → Privileged Gateway Intents (without it the bot fails to connect)

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
EIA_API_KEY=your_eia_api_key
```

`ADMIN_USER_ID` is your personal Discord user ID (enables `/setcount`). `UPTIME_KUMA_PUSH_URL` is optional; leave it out to skip status reporting. `EIA_API_KEY` is a free key from [EIA Open Data](https://www.eia.gov/opendata/); without it, the gas price response is skipped.

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

- Every push runs the tests, except pushes that only change Markdown or images.
- Pushes to `main` then deploy: `bot.py`, `responses.py` and `requirements.txt` are copied to the VM, `.env` is written from GitHub secrets, dependencies are installed, and the service is restarted. Overlapping deploys queue rather than run at once. The deploy fails if the bot doesn't log in within 30 seconds.
- Any branch can be deployed manually from the Actions tab by running the workflow with "Deploy this branch" checked.

Required GitHub secrets: `VM_HOST`, `VM_HOST_KEY`, `VM_SSH_KEY`, `DISCORD_TOKEN`, `ADMIN_USER_ID`, `EIA_API_KEY`, and optionally `UPTIME_KUMA_PUSH_URL`.

The live `counter.json` exists only on the VM and is not touched by deploys. To back it up:

```bash
scp ubuntu@<vm-host>:/opt/impeached-again-bot/counter.json .
```

If `counter.json` is ever lost, find the bot's last reply in each server and run `/setcount <number>` there.

### VM setup (one time)

Needed only when building a new VM. The deploy handles everything after this.

1. Install Python 3.14 (`python3.14` and its `venv` module).
2. Create the app directory: `sudo mkdir -p /opt/impeached-again-bot && sudo chown ubuntu: /opt/impeached-again-bot`
3. Make sure the `ubuntu` user can run `sudo systemctl restart impeached-again-bot` and `sudo journalctl -u impeached-again-bot` without a password; the deploy uses both. Oracle's Ubuntu image already grants `ubuntu` passwordless sudo for everything (`/etc/sudoers.d/90-cloud-init-users`), but the bot's own rule covers both commands in case that is ever removed. Create it with `sudo visudo -f /etc/sudoers.d/impeached-again-bot`:

   ```
   ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart impeached-again-bot, /usr/bin/journalctl -u impeached-again-bot *
   ```
4. Create `/etc/systemd/system/impeached-again-bot.service`:

   ```ini
   [Unit]
   Description=Impeached Again Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/opt/impeached-again-bot
   EnvironmentFile=/opt/impeached-again-bot/.env
   ExecStart=/opt/impeached-again-bot/venv/bin/python bot.py
   Restart=on-failure
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

5. Enable it: `sudo systemctl daemon-reload && sudo systemctl enable impeached-again-bot`
6. Set the `VM_HOST_KEY` GitHub secret to the VM's SSH host key, so deploys only connect to this VM. Run this on the VM and use the output line as the secret (the `*` matches any address, so it keeps working if the VM's IP changes; the key itself is what verifies the server):

   ```bash
   echo "* $(cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub)"
   ```

7. Run the GitHub Actions workflow on `main` to deploy the code, create the venv and start the bot.
