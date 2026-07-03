import asyncio
from app.server import api_run_pipeline

async def main():
    res = await api_run_pipeline("AAPL", 3)
    print("KEYS IN REPORT:", res.get("report", {}).keys())

asyncio.run(main())
