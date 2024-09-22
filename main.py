from objects.TodoistNotionSyncer import TodoistNotionSyncer
from objects.helpers.configuration import load_logging_config
import objects.helpers.cache as cache
import logging.config

if __name__ == "__main__":
    cache.create_tables()
    logging.config.dictConfig(load_logging_config())
    logging.info("Starting Syncer...")
    TodoistNotionSyncer().sync_todoist_to_notion()
    logging.info("Syncer done.")
