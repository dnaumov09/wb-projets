from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import traceback

import utils.logging_settings as logging_settings
from services import scheduler
from bot import bot
from web import webapp


async def restartable_task(name: str, create_task_fn):
    """Запускает задачу с бесконечным перезапуском при падении."""
    while True:
        try:
            logging.info(f"[{name}] starting...")
            await create_task_fn()
        except Exception:
            logging.exception(f"[{name}] crashed with exception:\n{traceback.format_exc()}")
            logging.info(f"[{name}] restarting in 5 seconds...")
            await asyncio.sleep(5)
        else:
            logging.info(f"[{name}] exited normally. Restarting in 5 seconds...")
            await asyncio.sleep(5)


async def main():
    scheduler.run_scheduler()

    bot_wrapper = restartable_task("bot", bot.create_bot_task)
    webapp_wrapper = restartable_task("webapp", webapp.create_server_task)

    await asyncio.gather(bot_wrapper, webapp_wrapper)


if __name__ == "__main__":
    logging_settings.init_logging(logging_settings.logging.INFO)
    asyncio.run(main())
