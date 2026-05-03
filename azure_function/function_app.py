import json
import os
from datetime import timedelta

import azure.durable_functions as df  # package: azure-functions-durable
import azure.functions as func
import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

myApp = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def _verify_signature(req: func.HttpRequest) -> bool:
    public_key = os.environ["DISCORD_PUBLIC_KEY"]
    signature = req.headers.get("X-Signature-Ed25519", "")
    timestamp = req.headers.get("X-Signature-Timestamp", "")
    try:
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
        key.verify(bytes.fromhex(signature), f"{timestamp}{req.get_body().decode()}".encode())
        return True
    except InvalidSignature:
        return False


@myApp.route(route="interactions", methods=["POST"])
@myApp.durable_client_input(client_name="client")
async def discord_interactions(
    req: func.HttpRequest, client
) -> func.HttpResponse:
    if not _verify_signature(req):
        return func.HttpResponse("Unauthorized", status_code=401)

    body = req.get_json()

    body_type = body.get("type")

    if body_type == 1:  # PING
        return func.HttpResponse(json.dumps({"type": 1}), mimetype="application/json")

    if body_type != 2 or body.get("data", {}).get("name") != "sleep":
        return func.HttpResponse("Unhandled", status_code=400)

    options = {
        opt["name"]: opt["value"]
        for opt in body["data"].get("options", [])
    }
    hours = int(options.get("hours", 0))
    minutes = int(options.get("minutes", 0))
    seconds = int(options.get("seconds", 0))
    total_seconds = hours * 3600 + minutes * 60 + seconds

    if total_seconds <= 0:
        return func.HttpResponse(
            json.dumps({
                "type": 4,
                "data": {
                    "content": "Specify a duration using `minutes` or `seconds`.",
                    "flags": 64,
                },
            }),
            mimetype="application/json",
        )

    await client.start_new(
        "sleep_orchestrator",
        None,
        {
            "user_id": body["member"]["user"]["id"],
            "guild_id": body["guild_id"],
            "total_seconds": total_seconds,
        },
    )

    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return func.HttpResponse(
        json.dumps({
            "type": 4,
            "data": {
                "content": f"Sleep timer set for {' and '.join(parts)}.",
                "flags": 64,
            },
        }),
        mimetype="application/json",
    )


@myApp.orchestration_trigger(context_name="context")
def sleep_orchestrator(context):
    data = context.get_input()
    deadline = context.current_utc_datetime + timedelta(seconds=data["total_seconds"])
    yield context.create_timer(deadline)
    yield context.call_activity("disconnect_user", data)


@myApp.activity_trigger(input_name="payload")
def disconnect_user(payload: dict):
    requests.patch(
        f"https://discord.com/api/v10/guilds/{payload['guild_id']}/members/{payload['user_id']}",
        headers={
            "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}",
            "Content-Type": "application/json",
        },
        json={"channel_id": None},
        timeout=10,
    )
