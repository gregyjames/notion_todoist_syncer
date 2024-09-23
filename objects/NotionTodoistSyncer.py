import logging
import NotionWrapper
from tinydb import Query
from helpers import cache
from NotionTask import NotionTask
from . import TodoistWrapper


class NotionTodoistSyncer:
    async def sync_notion_to_todoist():
        try:
            response = NotionWrapper.notion_api.databases.query(
                **{
                    "database_id": NotionWrapper.database_id,
                }
            )
            # Extract page information
            pages = response.get("results", [])
            for page in pages:
                page_id = page["id"]
                exists_in_todoist = Query()
                result = cache.db.search(exists_in_todoist.notion_task_id == page_id)
                if result == []:
                    task = NotionTask(page_id)
                    is_done = await task.get_tags_from_page()
                    if not is_done:
                        page_title = page["properties"]["Name"]["title"][0]["text"][
                            "content"
                        ]
                        logging.info(
                            f"Page ID: {page_id}, Page Title: {page_title}, Done: {is_done}"
                        )
                        todoist_id = TodoistWrapper.TodoistWrapper.add_task_to_todoist(
                            TodoistWrapper.project_id, str(page_title)
                        )
                        cache.add_to_task_cache(page_id, todoist_id)

        except Exception as e:
            logging.critical(f"An error occurred: {e}")
