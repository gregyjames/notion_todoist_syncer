from objects.TodoistNotionSyncer import TodoistNotionSyncer
from objects.helpers.configuration import load_logging_config
import logging.config
import json

if __name__ == "__main__":
    # sync_notion_to_todoist()
    logging.config.dictConfig(load_logging_config())
    logging.info("Starting Syncer...")
    TodoistNotionSyncer().sync_todoist_to_notion()
    logging.info("Syncer done.")
