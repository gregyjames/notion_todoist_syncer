import sqlite3
import logging
import os


def create_tables():
    """
    Creates the tables in the cache database if they are not found.
    """
    if not os.path.exists("cache.db"):
        logging.info("DB File does not exist, creating new one...")

    global conn
    global cursor

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name FROM sqlite_master WHERE type='table' AND name='Relation';
    """
    )
    table_exists = cursor.fetchone()

    if table_exists:
        logging.info("Tables already exist. No need to create them.")
        return

    logging.info("Creating Relation Table...")
    cursor.execute(
        """
        CREATE TABLE "Relation" (
	    "ID"	INTEGER NOT NULL UNIQUE,
	    "TodoistTaskID"	TEXT NOT NULL UNIQUE,
	    "NotionTaskID"	TEXT NOT NULL UNIQUE,
	    PRIMARY KEY("ID" AUTOINCREMENT)
        );
        """
    )
    logging.info("Created Relation Table.")
    cursor.execute(
        """
        CREATE TABLE "TodoistTasks" (
	    "ID"	TEXT UNIQUE,
	    "Title"	TEXT,
	    "RelationID"	INTEGER NOT NULL,
	    "Status"	TEXT,
	    PRIMARY KEY("ID")
        );
        """
    )
    logging.info("Created TodoistTasks Table.")
    cursor.execute(
        """
        CREATE TABLE "NotionTask" (
	    "ID"	TEXT,
	    "Title"	TEXT,
	    "DueDate"	TEXT NOT NULL,
	    "RelationID"	INTEGER NOT NULL,
	    "Status"	TEXT,
	    PRIMARY KEY("ID"),
	    FOREIGN KEY("RelationID") REFERENCES "Relation"("ID")
        );
        """
    )
    logging.info("Created NotionTask Table.")
    conn.commit()


def close_connection():
    """
    Closes the connection to the sqlite database.
    """
    cursor.close()
    conn.close()


def get_notion_task_from_todoist(todoist_id):
    """
    Gets the corresponding notion task id from a todoist task id.
    """
    cursor.execute(
        """
        SELECT NotionTaskID FROM Relation
        WHERE TodoistTaskID = ?
        """,
        (todoist_id,),
    )
    results = cursor.fetchall()
    # logging.info(f"{results}")
    if results == []:
        return ""
    else:
        return results[0][0]


def query_all_noncompleted_todoist_rows():
    """
    Gets all pending todoist rows from cache.
    """
    cursor.execute(
        """
        SELECT ID FROM TodoistTasks
        WHERE Status = "False"
        """
    )
    results = cursor.fetchall()
    return results


def update_status_from_todoist(todoist_id, notion_done_status):
    """
    Uses the completed todoist task id to updated the status of the corresponding notion and todoist tasks in the cache.
    """
    cursor.execute(
        """
        SELECT NotionTaskID FROM Relation
        WHERE TodoistTaskID = ?
        """,
        (todoist_id,),
    )
    results = cursor.fetchall()

    if len(results) == 0:
        print("No corresponding NotionTaskID found")
        return  # Exit if no result is found

    notion_id = results[0][0]

    # Update status in TodoistTasks table
    cursor.execute(
        """
        UPDATE TodoistTasks
        SET Status = 'True'
        WHERE ID = ?
        """,
        (todoist_id,),
    )
    conn.commit()  # Make sure the changes are committed

    # Update status in NotionTask table
    cursor.execute(
        """
        UPDATE NotionTask
        SET Status = ?
        WHERE ID = ?
        """,
        (
            str(notion_done_status),  # Ensure notion_done_status is passed or defined
            notion_id,
        ),
    )
    conn.commit()  # Commit changes to NotionTask


def get_todoist_task_from_notion(notion_id):
    """
    Gets the corresponding todoist task from the notion task id.
    """
    cursor.execute(
        """
        SELECT TodoistTaskID FROM Relation
        WHERE NotionTaskID = ?
        """,
        (notion_id),
    )
    results = cursor.fetchall()
    if results.count == 0:
        return -1
    else:
        return results[0]


def query_all_rows():
    """
    Returns all the note relations.
    """
    cursor.execute(
        """
        SELECT * FROM Relation
        """
    )
    results = cursor.fetchall()
    return results


def add_notion_task(id, title, duedate, relationid, status):
    """
    Adds a new notion task to the cache.
    """
    try:
        data = [(str(id), str(title), str(duedate), relationid, status)]
        cursor.executemany(
            """
        INSERT INTO NotionTask (ID, Title, DueDate, RelationID, Status) VALUES (?, ?, ?, ?, ?)
        """,
            data,
        )
        conn.commit()
    except Exception as error:
        logging.error(f"Error adding notion task: {error}")


def add_todoist_task(id, title, relationid, status):
    """
    Adds a new todoist task to the cache.
    """
    try:
        data = [(id, str(title), relationid, str(status))]
        cursor.executemany(
            """
        INSERT INTO TodoistTasks (ID, Title, RelationID, Status) VALUES (?, ?, ?, ?)
        """,
            data,
        )
        conn.commit()
    except Exception as error:
        logging.error(f"Error adding todoist task: {error}")


def add_to_task_cache(notion_task_id, todoist_id, notion_status, todoist_status):
    data = [(str(todoist_id), str(notion_task_id))]

    cursor.executemany(
        """
    INSERT INTO Relation (TodoistTaskID, NotionTaskID) VALUES (?, ?)
    """,
        data,
    )
    conn.commit()

    # last_id = cursor.lastrowid
    cursor.execute("SELECT MAX(ID) FROM Relation")
    last_id = cursor.fetchone()[0]

    return last_id


def delete_todoist_task(task_id):
    """
    Deletes a row from the TodoistTasks table based on the task ID.

    :param task_id: The ID of the task to be deleted.
    """
    cursor.execute(
        """
        DELETE FROM TodoistTasks
        WHERE ID = ?
        """,
        (task_id,),
    )

    # Commit the changes to the database
    conn.commit()
    logging.info(f"Todoist task with ID {task_id} deleted.")


def delete_notion_task(task_id):
    """
    Deletes a row from the NotionTasks table based on the task ID.

    :param task_id: The ID of the task to be deleted.
    """
    cursor.execute(
        """
        DELETE FROM NotionTask
        WHERE ID = ?
        """,
        (task_id,),
    )

    # Commit the changes to the database
    conn.commit()
    logging.info(f"Notion task with ID {task_id} deleted.")


def delete_relation_row(id):
    """
    Deletes a relation row based on the provided notion/todoist task id.
    """
    cursor.execute(
        """
        DELETE FROM Relation
        Where TodoistTaskID = ? or NotionTaskID = ?
        """,
        (
            str(id),
            str(id),
        ),
    )
    conn.commit()
