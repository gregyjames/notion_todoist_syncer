from objects.helpers import configuration
from objects.helpers import cache
from objects import NotionWrapper
from objects.TodoistWrapper import TodoistWrapper
from objects.NotionTask import NotionTask
import logging
import requests


class TodoistNotionSyncer:
    def __init__(self) -> None:
        self.new = 0
        self.updated = 0
        self.deleted = 0
        self.fail = 0

    def sync_todoist_to_notion(self):
        self.sync_deleted_todoist_tasks_notion()
        try:
            projects = TodoistWrapper.api.get_projects()
            for project in projects:
                logging.debug(project.name + " -> " + str(project.id))
            project = TodoistWrapper.api.get_project(configuration.project_id)

            logging.info("Processing tasks from Todoist...")

            for task in TodoistWrapper.get_tasks():
                logging.debug(f"Task ID: {task.id}")
                if task.isNewTask():
                    logging.info(f'New task "{task.title} {task.id}"')
                    notion_id = NotionWrapper.NotionWrapper.create_subpage_in_database(
                        task.title,
                        NotionWrapper.notion_default_status,
                        task.priority,
                        task.due,
                    )
                    relation_id = cache.add_to_task_cache(
                        notion_id,
                        task.id,
                        NotionWrapper.notion_default_status,
                        task.iscomplete,
                    )
                    logging.debug(f"Relation id: {relation_id}")
                    cache.add_notion_task(
                        notion_id,
                        task.title,
                        task.due,
                        relation_id,
                        NotionWrapper.notion_default_status,
                    )
                    cache.add_todoist_task(
                        task.id, task.title, relation_id, task.iscomplete
                    )
                    self.new += 1
                else:
                    # TODO: Add logic to update existing note tags here
                    if task.iscomplete:
                        logging.info(
                            f'Processing existing task "{task.title} {task.id}"'
                        )
                        notion_id = cache.get_notion_task_from_todoist(task.id)
                        notion_task = NotionTask(notion_id)
                        notion_task.update_select_tag_on_page(
                            notion_id, NotionWrapper.notion_done_status
                        )
                        self.updated += 1
            self.sync_todoist_completed_tasks_notion()
        except Exception as error:
            logging.critical(f"Error processing task #{task.id}: {error}")
            self.fail += 1
        self.sync_stats()

    def sync_todoist_completed_tasks_notion(self):
        """
        Syncs completed tasks from todoist to notion.
        """
        logging.info("Syncing completed tasks...")
        results = cache.query_all_noncompleted_todoist_rows()
        for result in results:
            try:
                task = TodoistWrapper.api.get_task(result[0])
                if task.is_completed:
                    notion_id = cache.get_notion_task_from_todoist(task.id)
                    if notion_id == "":
                        continue
                    note = NotionTask(notion_id)
                    note.update_select_tag_on_page(NotionWrapper.notion_done_status)
                    cache.update_status_from_todoist(
                        task.id, NotionWrapper.notion_done_status
                    )
                    self.updated += 1
            except Exception as e:
                logging.critical(f"Error updating todoist task #{result[0]}: {e}")
                self.fail += 1

    def sync_deleted_todoist_tasks_notion(self):
        """
        Syncs deleted tasks from todoist to notion.
        """
        logging.info("Syncing deleted tasks...")
        rows = cache.query_all_rows()
        for row in rows:
            try:
                TodoistWrapper.api.get_task(row[1])
            except requests.exceptions.HTTPError:
                # The api throws an error if the note isn't found
                notion_task = NotionTask(row[2])
                notion_task.archive_page()
                cache.delete_relation_row(row[1])
                cache.delete_notion_task(row[2])
                cache.delete_todoist_task(row[1])
                self.deleted += 1
            except Exception as e:
                logging.critical(f"Error deleting notion task {row[2]}: {e}")
                self.fail += 1

    def sync_stats(self):
        """
        Gets the sync stats for todoist to notion sync.
        """
        logging.info(
            f"TodoistNotionSync -> New: {self.new} -> Updated: {self.updated} -> Deleted: {self.deleted} -> Fail: {self.fail}"
        )
