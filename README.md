# Discord Sleep Timer

A Discord slash command that disconnects you from a voice channel after a set duration. No persistent server required — runs on Azure Functions.

```
/sleep hours:1
/sleep minutes:30
/sleep hours:1 minutes:30 seconds:30
```

Only the user who runs the command is disconnected. No one can use it to disconnect others.

## Discord Server Setup

### 1. Create a bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**
2. Go to the **Bot** tab → **Reset Token** → copy the token
3. Go to **General Information** → copy the **Public Key** and **Application ID**

### 2. Add the bot to your server

1. Go to **OAuth2 → URL Generator**
2. Check the **bot** scope
3. Check the **Move Members** permission
4. Open the generated URL and select your server

### 3. Configure and deploy

Fill in `.env` using `.env.example` as a template, deploy the Azure Function, and set the **Interactions Endpoint URL** in the Developer Portal to your function's URL.

### 4. Register the slash command

```powershell
pip install requests python-dotenv
python register_command.py
```

See [local testing instructions](azure_function/README.md) for development setup.
