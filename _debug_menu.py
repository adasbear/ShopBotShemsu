import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

# Simulate the exact API endpoint code
import database
database.init_db()
supabase = database._supabase

import asyncio

async def _db(callable):
    return await asyncio.to_thread(callable)

# Exact query from main.py
query = supabase.table("menu").select("name, price, parent")
query = query.order("parent", nullsfirst=True).order("name")

async def test():
    result = await _db(lambda: query.execute())
    enriched = []
    for idx, item in enumerate(result.data):
        enriched.append({
            "id": idx + 1,
            "name": item["name"],
            "price": float(item["price"]),
            "parent": item.get("parent"),
            "available": True
        })
    print(f'OK: {len(enriched)} items')
    for item in enriched[:3]:
        print(f'  {item}')

asyncio.run(test())
