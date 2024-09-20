import logging


class NotionTodoistSyncer:
    def sync_notion_to_todoist():
        try:
            response = notion_api.databases.query(
                **{
                    "database_id": database_id,
                }
            )
            # Extract page information
            pages = response.get("results", [])
            for page in pages:
                page_id = page["id"]
                exists_in_todoist = Query()
                result = db.search(exists_in_todoist.notion_task_id == page_id)
                if result == []:
                    is_done = get_tags_from_page(page_id=page_id)
                    if not is_done:
                        page_title = page["properties"]["Name"]["title"][0]["text"][
                            "content"
                        ]
                        print(
                            f"Page ID: {page_id}, Page Title: {page_title}, Done: {is_done}"
                        )
                        todoist_id = add_task_to_todoist(project_id, str(page_title))
                        add_to_task_cache(page_id, todoist_id)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
