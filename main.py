from todoist_api_python.api import TodoistAPI
from notion_client import Client
from tinydb import TinyDB, Query
import json
import requests

def read_json_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)  # Load the JSON data into a dictionary
            return config
    except FileNotFoundError:
        print(f"Configuration file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}.")
        return None

db = TinyDB('db.json')
config = read_json_config("config.json")

todoist_api_key = config.get("todoist_api_key")
notion_api_key = config.get("notion_api_key")
database_id = config.get("database_id")
project_id = config.get("project_id")
notion_status_tag_name = config.get("notion_status_tag_name")
notion_done_status = config.get("notion_done_status")
notion_default_status = config.get("notion_default_status")
todoist_notion_priority_map = {
    1: "None",
    2: "Low",
    3: "Medium",
    4: "High"
}

api = TodoistAPI(todoist_api_key)
notion_api = Client(auth=notion_api_key)

def get_tags_from_page(page_id) -> bool:
    try:
        # Retrieve the page properties
        page = notion_api.pages.retrieve(page_id=page_id)

        # Assuming the tags are stored in a property called "Status"
        select_property = page['properties'].get(notion_status_tag_name, {})

        if select_property['type'] == 'select':
            selected_tag = select_property['select']
            if selected_tag['name'] == notion_done_status:
                #print(f"Selected Tag: {selected_tag['name']}")
                return True
            else:
                #print("No tag is selected.")
                return False
        else:
            print("The property is not a select type.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def sync_notion_to_todoist():
    try:
        response = notion_api.databases.query(
            **{
                "database_id": database_id,
            }
        )
        # Extract page information
        pages = response.get('results', [])
        for page in pages:
            page_id = page['id']
            exists_in_todoist = Query()
            result = db.search(exists_in_todoist.notion_task_id == page_id)
            if result == []:
                is_done = get_tags_from_page(page_id=page_id)
                if not is_done:
                    page_title = page['properties']['Name']['title'][0]['text']['content']
                    print(f"Page ID: {page_id}, Page Title: {page_title}, Done: {is_done}")
                    todoist_id = add_task_to_todoist(project_id, str(page_title))
                    add_to_task_cache(page_id, todoist_id)
        
    except Exception as e:
        print(f"An error occurred: {e}")

def add_task_to_todoist(project_str, content_str) -> str:
    task = api.add_task(content=content_str, project=project_str, is_completed=False)
    return task.id

def create_subpage_in_database(title, status, priority) -> str:
    try:
        notion_priority = todoist_notion_priority_map[priority]
        # Create a new page (subpage) in the database
        new_page = notion_api.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                # Add other properties here (e.g., tags, status, etc.)
                # For example, adding a "Status" property (which is a select):
                "Status": {
                    "select": {
                        "name": status
                    }
                },
                "Priority": {
                    "select": {
                        "name": notion_priority
                    }
                }
            }
        )
        print(f"Subpage '{title}' created successfully with ID: {new_page['id']}")
        return new_page['id']
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def check_if_todoist_task_exists(page_id):
    exists_in_todoist = Query()
    result = db.search(exists_in_todoist.todoist_task_id == page_id)
    if result == []:
        return False
    else: 
        return True

def query_for_notion_id(todoist_id):
    notion_results = Query()
    result = db.search(exists_in_todoist.todoist_task_id == todoist_id)
    notion_id = result[0]['notion_task_id']
    return notion_id

def query_all_rows():
    return db.all()

def query_all_noncompleted_todoist_rows():
    Row = Query()
    results = db.search(Row.todoist_status == 'False')
    return results

def archive_page(page_id):
    try:
        # Archive (soft-delete) the page by setting 'archived' to True
        notion_api.pages.update(
            page_id=page_id,
            archived=True
        )
        print(f"Page {page_id} has been archived (soft-deleted).")
    except Exception as e:
        print(f"An error occurred: {e}")

def add_to_task_cache(notion_task_id, todoist_id, notion_status, todoist_status):
    db.insert(
        {
            'notion_task_id': str(notion_task_id), 
            'todoist_task_id': str(todoist_id),
            'notion_status': str(notion_status),
            'todoist_status': str(todoist_status)
        })

def update_select_tag_on_page(page_id, new_tag):
    try:
        # Update the page with a new tag in the 'Tags' property (select)
        notion_api.pages.update(
            page_id=page_id,
            properties={
                notion_status_tag_name: {
                    "select": {
                        "name": new_tag  # Update with a new single select tag
                    }
                }
            }
        )
        print(f"Tag updated successfully on page: {page_id}")
    except Exception as e:
        print(f"An error occurred: {e}")

def sync_todoist_to_notion():
    sync_deleted_todoist_tasks_notion()
    try:
        #projects = api.get_projects()
        #for project in projects:
        project = api.get_project(project_id)
        print(project.name + " -> " + str(project.id))
        tasks = api.get_tasks(project_id=project.id)
        for task in tasks:
            exists = check_if_todoist_task_exists(task.id)
            if not exists:
                notion_id = create_subpage_in_database(task.content, notion_default_status, task.priority)
                add_to_task_cache(notion_id, task.id, notion_default_status, task.is_completed)
                print("\t NEW TASK: " + task.content + " -> " + task.id + " -> " + str(task.is_completed))
            else:
                    print("\t FOUND TASK: " + task.content + " -> " + task.id + " -> " + str(task.is_completed))
                    '''
                    if task.is_completed == True:
                        notion_id = query_for_notion_id(task.id)
                        update_select_tag_on_page(notion_id, notion_done_status)
                    '''
            sync_todoist_completed_tasks_notion()
    except Exception as error:
        print(error)

def sync_todoist_completed_tasks_notion():
    results = query_all_noncompleted_todoist_rows()
    for result in results:
        task = api.get_task(result["todoist_task_id"])
        if task.is_completed:
            update_select_tag_on_page(result["notion_task_id"], notion_done_status)
            updated = result
            updated["notion_status"] = notion_done_status
            updated["todoist_status"] = str(True)
            db.update(updated)

def sync_deleted_todoist_tasks_notion():
    rows = query_all_rows()
    for row in rows:
        try:
            task = api.get_task(row["todoist_task_id"])
        except requests.exceptions.HTTPError as http_err:
            page = Query()
            archive_page(page.notion_task_id)
            db.remove(page.todoist_task_id == row["todoist_task_id"])

if __name__ == "__main__":
    #sync_notion_to_todoist()
    sync_todoist_to_notion()