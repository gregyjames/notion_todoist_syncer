from .helpers import configuration
from notion_client import Client
import logging
import tzlocal

notion_api_key = configuration.config.get("notion_api_key")
notion_api = Client(auth=notion_api_key)
notion_status_tag_name = configuration.config.get("notion_status_tag_name")
notion_done_status = configuration.config.get("notion_done_status")
notion_default_status = configuration.config.get("notion_default_status")

todoist_notion_priority_map = {1: "None", 2: "Low", 3: "Medium", 4: "High"}


class NotionWrapper:
    database_id = configuration.config.get("database_id")

    @classmethod
    def create_subpage_in_database(self, title, status, priority, due) -> str:
        try:
            notion_priority = todoist_notion_priority_map[priority]
            properties = {
                "Name": {"title": [{"text": {"content": title}}]},
                "Status": {"select": {"name": status}},
                "Priority": {"select": {"name": notion_priority}},
            }

            if due is not None:
                # Uses localtime zone to set due time of new note
                local_timezone = tzlocal.get_localzone()
                properties["Due Date"] = {
                    "date": {"start": due, "time_zone": str(local_timezone)}
                }

            # Create a new page (subpage) in the database
            new_page = notion_api.pages.create(
                parent={"database_id": NotionWrapper.database_id},
                properties=(properties),
            )

            logging.info(
                f"Subpage '{title}' created successfully with ID: {new_page['id']}"
            )
            return new_page["id"]
        except Exception as e:
            logging.error(
                f"An error occurred creating page in notion for task '{title}': {e}"
            )
            return ""
