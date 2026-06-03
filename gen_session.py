import asyncio
import sys

API_ID = int(sys.argv[1]) if len(sys.argv) > 1 else int(input("API ID: "))
API_HASH = sys.argv[2] if len(sys.argv) > 2 else input("API HASH: ")
PHONE = sys.argv[3] if len(sys.argv) > 3 else input("Phone (+251...): ")

async def main():
    from pyrogram import Client
    client = Client("gen_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE, in_memory=True)
    await client.start()
    session_str = await client.export_session_string()
    print("\n" + "=" * 60)
    print("PYRO_SESSION_STRING (copy this to Render env vars):")
    print("=" * 60)
    print(session_str)
    print("=" * 60 + "\n")
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
