from . import NotionWrapper
import logging
from notion_client import APIResponseError
from .helpers import cache


class NotionTask:
    def __init__(self, id):
        self.note_id = id

    async def get_tags_from_page(self) -> bool:
        try:
            # Retrieve the page properties
            page = await NotionWrapper.notion_api.pages.retrieve(page_id=self.note_id)

            # Assuming the tags are stored in a property called "Status"
            select_property = page["properties"].get(
                NotionWrapper.notion_status_tag_name, {}
            )

            if select_property["type"] == "select":
                selected_tag = select_property["select"]
                if selected_tag["name"] == NotionWrapper.notion_done_status:
                    logging.debug(f"Task {self.note_id} is completed.")
                    return True
                else:
                    logging.debug(f"Task {self.note_id} doesn't have selected tag.")
                    return False
            else:
                logging.error(
                    f"The completion property on task {self.note_id} is not a select type."
                )
                return False
        except Exception as e:
            logging.critical(f"An error occurred: {e}")
            return False

    async def update_select_tag_on_page(self, new_tag):
        try:
            # Update the page with a new tag in the 'Tags' property (select)
            await NotionWrapper.notion_api.pages.update(
                page_id=self.note_id,
                properties={
                    NotionWrapper.notion_status_tag_name: {
                        "select": {
                            "name": new_tag  # Update with a new single select tag
                        }
                    }
                },
            )
            logging.info(
                f"Tag updated successfully on task #{self.note_id} to {new_tag}."
            )
        except Exception as e:
            logging.critical(
                f"An error occurred updating tag on task #{self.note_id}: {e}"
            )

    def archive_page(self):
        try:
            # Archive (soft-delete) the page by setting 'archived' to True
            NotionWrapper.notion_api.pages.update(page_id=self.note_id, archived=True)
            logging.info(f"Task {self.note_id} has been archived (soft-deleted).")
        except APIResponseError as e:
            logging.error(
                f"{e} -> Looks like the notion task #{self.note_id} was deleted, deleting it from cache..."
            )
            cache.delete_notion_task(self.note_id)
        except Exception as e:
            logging.critical(f"An error occurred archieving task #{self.note_id}: {e}")
