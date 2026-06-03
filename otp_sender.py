import asyncio
import logging

from config import PYRO_API_ID, PYRO_API_HASH, PYRO_PHONE, PYRO_SESSION_STRING

_client = None

async def get_client():
    global _client
    if _client:
        return _client
    from pyrogram import Client
    kwargs = dict(api_id=PYRO_API_ID, api_hash=PYRO_API_HASH, in_memory=True)
    if PYRO_SESSION_STRING:
        kwargs["session_string"] = PYRO_SESSION_STRING
    else:
        kwargs["phone_number"] = PYRO_PHONE
    _client = Client("shemsu_otp", **kwargs)
    await _client.start()
    if not PYRO_SESSION_STRING:
        exported = await _client.export_session_string()
        logging.warning(f"PYRO_SESSION_STRING (save this to env vars): {exported}")
    return _client


async def send_otp(username, otp_code):
    client = await get_client()
    text = f"Your Shemsu Shop login code: {otp_code}\n\nExpires in 5 minutes."
    try:
        await client.send_message(username, text)
        logging.info(f"OTP sent to @{username}")
        return True
    except Exception as e:
        logging.error(f"Failed to send OTP to @{username}: {e}")
        return False
