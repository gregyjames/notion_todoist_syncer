from tinydb import TinyDB, Query

db = TinyDB("db.json")


def check_if_todoist_task_exists(page_id):
    exists_in_todoist = Query()
    result = db.search(exists_in_todoist.todoist_task_id == page_id)
    if result == []:
        return False
    else:
        return True


def query_all_rows():
    return db.all()


def query_all_noncompleted_todoist_rows():
    Row = Query()
    results = db.search(Row.todoist_status == "False")
    return results


def query_for_notion_id(todoist_id):
    notion_results = Query()
    result = db.search(notion_results.todoist_task_id == todoist_id)
    notion_id = result[0]["notion_task_id"]
    return notion_id


def add_to_task_cache(notion_task_id, todoist_id, notion_status, todoist_status):
    db.insert(
        {
            "notion_task_id": str(notion_task_id),
            "todoist_task_id": str(todoist_id),
            "notion_status": str(notion_status),
            "todoist_status": str(todoist_status),
        }
    )
