from .helpers import configuration
from todoist_api_python.api import TodoistAPI
from dataclasses import dataclass
from .helpers import cache
from datetime import datetime, timezone

todoist_api_key = configuration.config.get("todoist_api_key")
project_id = configuration.config.get("project_id")


@dataclass
class TodoistTask:
    id: int
    iscomplete: bool
    title: str
    priority: int
    due: str

    async def isNewTask(self) -> bool:
        return await cache.get_notion_task_from_todoist(self.id) == ""


def convert_to_rfc3339(date_string):
    # Parse the date string (YYYY-MM-DD) to a datetime object
    dt = datetime.strptime(date_string, "%Y-%m-%d")

    # Set the time to midnight and set the timezone to UTC
    dt_utc = dt.replace(tzinfo=timezone.utc)

    # Return the datetime in RFC3339 format
    return dt_utc.isoformat()


class TodoistWrapper:
    api = TodoistAPI(todoist_api_key)

    def __init__(self):
        pass

    async def add_task_to_todoist(self, project_str, content_str) -> str:
        """
        Adds a new task to the todoist project.
        """
        task = await self.api.add_task(
            content=content_str, project=project_str, is_completed=False
        )
        return task.id

    @classmethod
    def get_tasks(self):
        """
        Generator method to wrap and get tasks from todoist.
        """
        for task in TodoistWrapper.api.get_tasks(project_id=project_id):
            due_date = None

            if task.due is not None and hasattr(task.due, "datetime"):
                due_date = task.due.datetime
            else:
                # TODO: Add logic for handling date only tasks (After the doist team addresses issue #157)
                """
                try:
                    # due_date = task.due.date + "T00:00:00"
                    due_date = convert_to_rfc3339(task.due.date)
                except:
                    print(task.due)
                """
                pass

            yield TodoistTask(
                task.id, task.is_completed, task.content, task.priority, due_date
            )
