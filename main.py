import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.blocking import BlockingScheduler

from db import init_db, complete_events
from handlers import bot, router

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
logging.basicConfig(level=logging.INFO)


scheduler = BlockingScheduler()
scheduler.add_job(complete_events, 'interval', days=1)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    init_db()
    asyncio.run(main())
    scheduler.start()