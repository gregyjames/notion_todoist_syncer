from .helpers import configuration
from todoist_api_python.api import TodoistAPI
from dataclasses import dataclass
from .helpers import cache

todoist_api_key = configuration.config.get("todoist_api_key")
project_id = configuration.config.get("project_id")


@dataclass
class TodoistTask:
    id: int
    iscomplete: bool
    title: str
    priority: int

    def isNewTask(self) -> bool:
        # logging.info(f"{cache.get_notion_task_from_todoist(self.id) == ""}")
        return cache.get_notion_task_from_todoist(self.id) == ""


class TodoistWrapper:
    api = TodoistAPI(todoist_api_key)

    def __init__(self):
        pass

    def add_task_to_todoist(self, project_str, content_str) -> str:
        task = self.api.add_task(
            content=content_str, project=project_str, is_completed=False
        )
        return task.id

    @classmethod
    def get_tasks(self):
        for task in TodoistWrapper.api.get_tasks(project_id=project_id):
            yield TodoistTask(task.id, task.is_completed, task.content, task.priority)
