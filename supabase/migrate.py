import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import pathlib

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file.")
    exit(1)

async def run_migration():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        schema_path = pathlib.Path(__file__).parent / "schema.sql"
        sql = schema_path.read_text(encoding="utf-8")
        await conn.execute(sql)
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        await conn.close()

asyncio.run(run_migration())
