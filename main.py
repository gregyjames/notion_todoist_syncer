from objects.TodoistNotionSyncer import TodoistNotionSyncer
from objects.helpers.configuration import load_logging_config
import objects.helpers.cache as cache
import objects.helpers.configuration as config
import logging.config
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


sync_schedule = config.config["cron"]

todoistnotionsyncer = TodoistNotionSyncer()


def todoist_notion_sync_task():
    logging.info("Running scheduled task to sync todoist to notion...")
    cache.init_connection()
    todoistnotionsyncer.sync_todoist_to_notion()
    cache.close_connection()
    logging.info("Syncer done.")


scheduler = BlockingScheduler()

scheduler.add_job(
    todoist_notion_sync_task,
    CronTrigger.from_crontab(sync_schedule),
    id="todoist_notion_sync_task",
    replace_existing=True,
)


if __name__ == "__main__":
    logging.config.dictConfig(load_logging_config())
    try:
        cache.init_connection()
        cache.create_tables()
        cache.close_connection()
        logging.info("Scheduler started. Press Ctrl+C to exit.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Scheduler ended.")
