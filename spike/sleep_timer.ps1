param(
    [int]$Hours = 0,
    [int]$Minutes = 0,
    [int]$Seconds = 5
)

$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim())
        }
    }
}

$BotToken = $env:DISCORD_BOT_TOKEN
$GuildId  = $env:DISCORD_GUILD_ID
$UserId   = $env:DISCORD_USER_ID

foreach ($var in @("DISCORD_BOT_TOKEN", "DISCORD_GUILD_ID", "DISCORD_USER_ID")) {
    if (-not [System.Environment]::GetEnvironmentVariable($var)) {
        Write-Error "$var is not set in .env"
        exit 1
    }
}

$seconds = ($Hours * 3600) + ($Minutes * 60) + $Seconds

if ($seconds -le 0) {
    Write-Error "Specify a duration: -Hours 1  -Minutes 30  -Seconds 90"
    exit 1
}

$parts = @()
if ($Hours)   { $parts += "$Hours hour$(if ($Hours -ne 1) { 's' })" }
if ($Minutes) { $parts += "$Minutes minute$(if ($Minutes -ne 1) { 's' })" }
if ($Seconds) { $parts += "$Seconds second$(if ($Seconds -ne 1) { 's' })" }
$display = $parts -join " and "

$memberJson = curl.exe -s -w "`n%{http_code}" `
    -H "Authorization: Bot $BotToken" `
    "https://discord.com/api/v10/guilds/$GuildId/members/$UserId"
$memberStatus = ($memberJson -split "`n")[-1]
$memberBody   = ($memberJson -split "`n")[0] | ConvertFrom-Json

if ($memberStatus -ne "200") {
    Write-Error "Could not fetch member — API error $memberStatus`: $($memberBody | ConvertTo-Json)"
    exit 1
}
Write-Host "Found member: $($memberBody.user.username) (ID: $($memberBody.user.id))"

Write-Host "Sleep timer started. Disconnecting in $display..."
Write-Host "Press Ctrl+C to cancel."

Start-Sleep -Seconds $seconds

$response = curl.exe -s -o NUL -w "%{http_code}" `
    -X PATCH `
    -H "Authorization: Bot $BotToken" `
    -H "Content-Type: application/json" `
    -d '{"channel_id": null}' `
    "https://discord.com/api/v10/guilds/$GuildId/members/$UserId"

if ($response -eq "200") {
    Write-Host "Disconnected."
} else {
    Write-Error "Discord API error $response"
}
