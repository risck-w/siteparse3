import time
from db.celery import app
import asyncio


async def sum(x, y):
    await asyncio.sleep(5)
    return x+y


@app.task
def hello(x, y):
    return asyncio.run(sum(x, y))
