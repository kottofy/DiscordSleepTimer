# Local Testing

## Prerequisites

```powershell
npm install -g azure-functions-core-tools@4
npm install -g azurite
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `local.settings.json` from `.env.example` values and fill in `DISCORD_BOT_TOKEN`, `DISCORD_PUBLIC_KEY`, and `DISCORD_APP_ID`.

## Run (3 terminals)

```powershell
# Terminal 1
azurite --location .azurite

# Terminal 2
.venv\Scripts\Activate.ps1 && func start

# Terminal 3
ngrok http 7071
```

Set the ngrok `https://` URL as the Interactions Endpoint URL in the Discord Developer Portal, then use `/sleep` in your server to test.

## Deploy

```powershell
az login
.venv\Scripts\Activate.ps1
func azure functionapp publish <your-app-name>
```
