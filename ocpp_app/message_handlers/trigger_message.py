# trigger_message.py
async def handle_trigger_message(payload):
    requested_message = payload.get("requestedMessage")
    if not requested_message:
        return {"status": "Rejected", "error": "MissingRequestedMessage"}

    # Implement logic to trigger the requested message
    trigger_requested_message(requested_message)
    return {"status": "Accepted"}
