from . import NotionTask
from .helpers import configuration
from notion_client import Client
import logging

notion_api_key = configuration.config.get("notion_api_key")
notion_api = Client(auth=notion_api_key)
notion_status_tag_name = configuration.config.get("notion_status_tag_name")
notion_done_status = configuration.config.get("notion_done_status")
notion_default_status = configuration.config.get("notion_default_status")

todoist_notion_priority_map = {1: "None", 2: "Low", 3: "Medium", 4: "High"}


class NotionWrapper:
    database_id = configuration.config.get("database_id")

    @classmethod
    def create_subpage_in_database(self, title, status, priority) -> str:
        try:
            notion_priority = todoist_notion_priority_map[priority]
            # Create a new page (subpage) in the database
            new_page = notion_api.pages.create(
                parent={"database_id": NotionWrapper.database_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    # Add other properties here (e.g., tags, status, etc.)
                    # For example, adding a "Status" property (which is a select):
                    "Status": {"select": {"name": status}},
                    "Priority": {"select": {"name": notion_priority}},
                },
            )

            logging.info(
                f"Subpage '{title}' created successfully with ID: {new_page['id']}"
            )
            return new_page["id"]
        except Exception as e:
            print(f"An error occurred creating page in notion for task '{title}': {e}")
            return ""
