# Discord Sleep Timer

A Discord slash command (`/sleep`) that disconnects you from a voice channel after a set duration. Built with Azure Durable Functions — no persistent server required.

## How it works

1. User runs `/sleep hours:1` in Discord
2. Discord sends an HTTP request to the Azure Function
3. A durable timer waits the specified duration
4. The bot disconnects the invoking user from voice

Users can only disconnect themselves — the target is always the user who typed the command.

## Prerequisites

- [Python 3.11+](https://www.python.org/)
- [Node.js](https://nodejs.org/) (for Azure Functions Core Tools and Azurite)
- [ngrok](https://ngrok.com/) account and CLI
- A Discord application with a bot and **Move Members** permission in your server

## Setup

### 1. Install tools

```powershell
npm install -g azure-functions-core-tools@4
npm install -g azurite
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in the values:

```
DISCORD_BOT_TOKEN=     # Developer Portal → your app → Bot → Token
DISCORD_GUILD_ID=      # Right-click server icon → Copy Server ID
DISCORD_USER_ID=       # Right-click yourself → Copy User ID
DISCORD_PUBLIC_KEY=    # Developer Portal → your app → General Information → Public Key
DISCORD_APP_ID=        # Developer Portal → your app → General Information → Application ID
```

Copy `azure_function/local.settings.json` from the example and fill in the same values:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DISCORD_BOT_TOKEN": "",
    "DISCORD_PUBLIC_KEY": "",
    "DISCORD_APP_ID": ""
  }
}
```

### 3. Set up the virtual environment

```powershell
cd azure_function
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Register the `/sleep` slash command

From the project root with the venv active:

```powershell
pip install python-dotenv requests
python register_command.py
```

This only needs to be run once. Guild commands are available immediately.

---

## Local testing with Azurite and ngrok

You need three terminals open.

### Terminal 1 — Azurite (local storage emulator)

```powershell
azurite --location .azurite
```

### Terminal 2 — Azure Function

```powershell
cd azure_function
.venv\Scripts\Activate.ps1
func start
```

Confirm the output lists `discord_interactions`, `sleep_orchestrator`, and `disconnect_user`.

### Terminal 3 — ngrok tunnel

```powershell
ngrok http 7071
```

Copy the `https://` forwarding URL (e.g. `https://abc123.ngrok-free.app`).

### Connect Discord to your local function

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → your app → **General Information**
2. Set **Interactions Endpoint URL** to `https://<ngrok-id>.ngrok-free.app/api/interactions`
3. Click Save — Discord will send a PING to verify

### Test

Join a voice channel in your Discord server and run:

```
/sleep minutes:1
```

You should receive an ephemeral confirmation message and be disconnected after 1 minute.

---

## Deploying to Azure

```powershell
az login
cd azure_function
.venv\Scripts\Activate.ps1
func azure functionapp publish <your-app-name>
```

After deploying, update the Interactions Endpoint URL in the Discord Developer Portal to your Azure function URL:

```
https://<your-app-name>.azurewebsites.net/api/interactions
```
