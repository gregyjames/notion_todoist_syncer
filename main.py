from objects.TodoistNotionSyncer import TodoistNotionSyncer
from objects.helpers.configuration import load_logging_config
import objects.helpers.cache as cache
import objects.helpers.configuration as config
import logging.config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

sync_schedule = config.config["cron"]

todoistnotionsyncer = TodoistNotionSyncer()


async def todoist_notion_sync_task():
    logging.info("Running scheduled task to sync todoist to notion...")
    await cache.init_connection()
    await todoistnotionsyncer.sync_todoist_to_notion()
    await cache.close_connection()
    logging.info("Syncer done.")


scheduler = AsyncIOScheduler()

scheduler.add_job(
    todoist_notion_sync_task,
    CronTrigger.from_crontab(sync_schedule),
    id="todoist_notion_sync_task",
    replace_existing=True,
)


async def main():
    logging.config.dictConfig(load_logging_config())
    try:
        await cache.init_connection()
        await cache.create_tables()
        await cache.close_connection()
        logging.info("Scheduler started. Press Ctrl+C to exit.")
        scheduler.start()
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit, asyncio.exceptions.CancelledError):
        logging.error("Scheduler ended.")
        pass


if __name__ == "__main__":
    asyncio.run(main())
