#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo "Creating .env..."
    read -p "DISCORD_TOKEN: " token
    read -p "ADMIN_USER_ID: " admin_id
    echo "DISCORD_TOKEN=$token" > .env
    echo "ADMIN_USER_ID=$admin_id" >> .env
fi

if [ ! -f counter.json ]; then
    echo '{"count": 0}' > counter.json
fi

bash deploy.sh
