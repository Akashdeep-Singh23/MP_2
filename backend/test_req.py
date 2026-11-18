import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
import httpx

async def main():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/health")
        print("API readiness:", r.status_code, r.json())

if __name__ == "__main__":
    asyncio.run(main())
