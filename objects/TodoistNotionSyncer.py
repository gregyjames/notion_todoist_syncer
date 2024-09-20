from objects.helpers import configuration
from objects.helpers import cache
from objects.helpers import configuration
from objects.helpers import cache
from objects import NotionWrapper
from objects.TodoistWrapper import TodoistWrapper
from objects.NotionTask import NotionTask
import logging


class TodoistNotionSyncer:
    def sync_todoist_to_notion(self):
        self.sync_deleted_todoist_tasks_notion()
        try:
            projects = TodoistWrapper.api.get_projects()
            for project in projects:
                logging.debug(project.name + " -> " + str(project.id))
            project = TodoistWrapper.api.get_project(configuration.project_id)

            logging.info("Processing tasks from Todoist...")
            tasks = TodoistWrapper.get_tasks()

            for task in tasks:
                exists = task.isNewTask()
                if not exists:
                    logging.info(f'New task "{task.title} {task.id}"')
                    notion_id = NotionWrapper.NotionWrapper.create_subpage_in_database(
                        task.title, NotionWrapper.notion_default_status, task.priority
                    )
                    cache.add_to_task_cache(
                        notion_id,
                        task.id,
                        NotionWrapper.notion_default_status,
                        task.iscomplete,
                    )
                else:
                    logging.info(f'Processing existing task "{task.title} {task.id}"')
                    if task.iscomplete == True:
                        notion_id = cache.query_for_notion_id(task.id)
                        notion_task = NotionTask(notion_id)
                        notion_task.update_select_tag_on_page(
                            notion_id, notion_done_status
                        )
            self.sync_todoist_completed_tasks_notion()
        except Exception as error:
            logging.error(error)

    def sync_todoist_completed_tasks_notion(self):
        results = cache.query_all_noncompleted_todoist_rows()
        for result in results:
            task = TodoistWrapper.api.get_task(result["todoist_task_id"])
            if task.is_completed:
                note = NotionTask(result["notion_task_id"])
                task = note.update_select_tag_on_page(NotionWrapper.notion_done_status)
                updated = result
                updated["notion_status"] = NotionWrapper.notion_done_status
                updated["todoist_status"] = str(True)
                cache.db.update(updated)

    def sync_deleted_todoist_tasks_notion(self):
        rows = cache.query_all_rows()
        for row in rows:
            try:
                pass
                # task = TodoistWrapper.api.get_task(row["todoist_task_id"])
            except requests.exceptions.HTTPError as http_err:
                page = Query()
                archive_page(page.notion_task_id)
                db.remove(page.todoist_task_id == row["todoist_task_id"])
