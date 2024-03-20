# reset.py
async def handle_reset(payload):
    type = payload.get("type")
    if type not in ["Hard", "Soft"]:
        return {"status": "Rejected", "error": "InvalidResetType"}

    # Implement logic to perform the reset based on the type
    perform_reset(type)
    return {"status": "Accepted"}
