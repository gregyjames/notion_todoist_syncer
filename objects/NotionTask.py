from . import NotionWrapper


class NotionTask:
    def __init__(self, id):
        self.note_id = id

    def get_tags_from_page(self) -> bool:
        try:
            # Retrieve the page properties
            page = NotionWrapper.notion_api.pages.retrieve(page_id=note_id)

            # Assuming the tags are stored in a property called "Status"
            select_property = page["properties"].get(
                NotionWrapper.notion_status_tag_name, {}
            )

            if select_property["type"] == "select":
                selected_tag = select_property["select"]
                if selected_tag["name"] == notion_done_status:
                    logging.debug(f"Task {self.note_id} is completed.")
                    return True
                else:
                    logging.debug(f"Task {self.note_id} doesn't have selected tag.")
                    return False
            else:
                logging.info(
                    f"The completion property on task {self.note_id} is not a select type."
                )
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def update_select_tag_on_page(self, new_tag):
        try:
            # Update the page with a new tag in the 'Tags' property (select)
            NotionWrapper.notion_api.pages.update(
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
            logging.error(
                f"An error occurred updating tag on task #{self.note_id}: {e}"
            )

    def archive_page(self):
        try:
            # Archive (soft-delete) the page by setting 'archived' to True
            NotionWrapper.notion_api.pages.update(page_id=self.note_id, archived=True)
            logging.info(f"Task {self.note_id} has been archived (soft-deleted).")
        except Exception as e:
            print(f"An error occurred archieving task #{self.note_id}: {e}")
