"""
Run once to register the /sleep slash command with Discord.
Guild commands are available immediately; global commands take up to 1 hour.

Usage:
    pip install requests python-dotenv
    python register_command.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.environ["DISCORD_APP_ID"]
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

command = {
    "name": "sleep",
    "description": "Disconnect yourself from voice after a set time",
    "options": [
        {
            "name": "hours",
            "description": "Hours to wait before disconnecting",
            "type": 4,
            "required": False,
            "min_value": 1,
            "max_value": 8,
        },
        {
            "name": "minutes",
            "description": "Minutes to wait before disconnecting",
            "type": 4,
            "required": False,
            "min_value": 1,
            "max_value": 59,
        },
        {
            "name": "seconds",
            "description": "Additional seconds to wait",
            "type": 4,
            "required": False,
            "min_value": 1,
            "max_value": 59,
        },
    ],
}

if GUILD_ID:
    url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{GUILD_ID}/commands"
else:
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"

response = requests.post(
    url,
    headers={"Authorization": f"Bot {BOT_TOKEN}"},
    json=command,
)

print(response.status_code, response.json())
