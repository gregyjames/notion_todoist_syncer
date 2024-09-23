# import sqlite3
import logging
import os
import aiosqlite

conn = None
cursor = None


async def init_connection():
    """
    Initializes a persistent connection and cursor.
    """
    global conn
    global cursor

    conn = await aiosqlite.connect("cache.db")
    cursor = await conn.cursor()
    # SET WAL mode
    await cursor.execute("PRAGMA journal_mode=WAL;")
    current_mode = (await cursor.fetchone())[0]
    logging.debug(f"Current journal mode: {current_mode}")
    # SET Locking mode to exclusive
    await cursor.execute("PRAGMA locking_mode=EXCLUSIVE;")
    locking_mode = (await cursor.fetchone())[0]
    logging.debug(f"Current locking mode: {locking_mode}")
    await cursor.execute("PRAGMA cache_size = -20000;")
    await cursor.execute("PRAGMA synchronous=OFF;")
    logging.info("Database connection established.")


async def create_tables():
    """
    Creates the tables in the cache database if they are not found.
    """
    if not os.path.exists("cache.db"):
        logging.info("DB File does not exist, creating new one...")

    await cursor.execute(
        """
        SELECT name FROM sqlite_master WHERE type='table' AND name='Relation';
        """
    )
    table_exists = await cursor.fetchone()

    if table_exists:
        logging.info("Tables already exist. No need to create them.")
        return

    # Enable FULL auto_vacuum if it's not already set
    await cursor.execute("PRAGMA auto_vacuum;")
    current_mode = (await cursor.fetchone())[0]

    if current_mode != 1:  # 1 means FULL auto_vacuum
        logging.info("Enabling FULL auto_vacuum mode...")
        await cursor.execute("PRAGMA auto_vacuum = FULL;")
        await cursor.execute("VACUUM;")  # Apply the change by vacuuming the database
        await conn.commit()

    logging.info("Creating tables and indexes...")
    await cursor.executescript(
        """
        -- Create Relation table
        CREATE TABLE IF NOT EXISTS "Relation" (
        "ID"	INTEGER NOT NULL UNIQUE,
        "TodoistTaskID"	TEXT NOT NULL UNIQUE,
        "NotionTaskID"	TEXT NOT NULL UNIQUE,
        PRIMARY KEY("ID" AUTOINCREMENT)
        );

        -- Create indexes for Relation table
        CREATE INDEX IF NOT EXISTS idx_relation_todoist
        ON Relation (TodoistTaskID);

        CREATE INDEX IF NOT EXISTS idx_relation_notion
        ON Relation (NotionTaskID);

        -- Create TodoistTasks table
        CREATE TABLE IF NOT EXISTS "TodoistTasks" (
        "ID"	TEXT UNIQUE,
        "Title"	TEXT,
        "RelationID"	INTEGER NOT NULL,
        "Status"	TEXT,
        PRIMARY KEY("ID")
        );

        -- Create index for TodoistTasks table
        CREATE INDEX IF NOT EXISTS idx_todoist_status
        ON TodoistTasks (Status);

        -- Create NotionTask table
        CREATE TABLE IF NOT EXISTS "NotionTask" (
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
    await conn.commit()
    logging.info("Tables and indexes created successfully.")


async def close_connection():
    """
    Closes the connection to the sqlite database.
    """
    if cursor is not None:
        await cursor.close()
    if conn is not None:
        await conn.close()
    logging.info("Database connection closed.")


async def get_notion_task_from_todoist(todoist_id):
    """
    Gets the corresponding notion task id from a todoist task id.
    """
    await cursor.execute(
        """
        SELECT NotionTaskID FROM Relation
        WHERE TodoistTaskID = ?
        """,
        (todoist_id,),
    )
    results = await cursor.fetchall()
    # logging.info(f"{results}")
    if results == []:
        return ""
    else:
        return results[0][0]


async def query_all_noncompleted_todoist_rows():
    """
    Gets all pending todoist rows from cache.
    """
    await cursor.execute(
        """
        SELECT ID FROM TodoistTasks
        WHERE Status = "False"
        """
    )
    results = await cursor.fetchall()
    return results


async def update_status_from_todoist(todoist_id, notion_done_status):
    """
    Uses the completed todoist task id to updated the status of the corresponding notion and todoist tasks in the cache.
    """
    await cursor.execute(
        """
        SELECT NotionTaskID FROM Relation
        WHERE TodoistTaskID = ?
        """,
        (todoist_id,),
    )
    results = await cursor.fetchall()

    if len(results) == 0:
        print("No corresponding NotionTaskID found")
        return  # Exit if no result is found

    notion_id = results[0][0]

    # Update status in TodoistTasks table
    await cursor.execute(
        """
        UPDATE TodoistTasks
        SET Status = 'True'
        WHERE ID = ?
        """,
        (todoist_id,),
    )
    await conn.commit()  # Make sure the changes are committed

    # Update status in NotionTask table
    await cursor.execute(
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
    await conn.commit()  # Commit changes to NotionTask


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


async def query_all_rows():
    """
    Returns all the note relations.
    """
    await cursor.execute(
        """
        SELECT * FROM Relation
        """
    )
    results = await cursor.fetchall()
    return results


async def add_notion_task(id, title, duedate, relationid, status):
    """
    Adds a new notion task to the cache.
    """
    try:
        data = [(str(id), str(title), str(duedate), relationid, status)]
        await cursor.executemany(
            """
        INSERT INTO NotionTask (ID, Title, DueDate, RelationID, Status) VALUES (?, ?, ?, ?, ?)
        """,
            data,
        )
        await conn.commit()
    except Exception as error:
        logging.error(f"Error adding notion task: {error}")


async def add_todoist_task(id, title, relationid, status):
    """
    Adds a new todoist task to the cache.
    """
    try:
        data = [(id, str(title), relationid, str(status))]
        await cursor.executemany(
            """
        INSERT INTO TodoistTasks (ID, Title, RelationID, Status) VALUES (?, ?, ?, ?)
        """,
            data,
        )
        await conn.commit()
    except Exception as error:
        logging.error(f"Error adding todoist task: {error}")


async def add_to_task_cache(notion_task_id, todoist_id, notion_status, todoist_status):
    data = [(str(todoist_id), str(notion_task_id))]

    await cursor.executemany(
        """
    INSERT INTO Relation (TodoistTaskID, NotionTaskID) VALUES (?, ?)
    """,
        data,
    )
    await conn.commit()

    # last_id = cursor.lastrowid
    await cursor.execute("SELECT MAX(ID) FROM Relation")
    last_id = (await cursor.fetchone())[0]

    return last_id


async def delete_todoist_task(task_id):
    """
    Deletes a row from the TodoistTasks table based on the task ID.

    :param task_id: The ID of the task to be deleted.
    """
    await cursor.execute(
        """
        DELETE FROM TodoistTasks
        WHERE ID = ?
        """,
        (task_id,),
    )

    # Commit the changes to the database
    await conn.commit()
    logging.info(f"Todoist task with ID {task_id} deleted.")


async def delete_notion_task(task_id):
    """
    Deletes a row from the NotionTasks table based on the task ID.

    :param task_id: The ID of the task to be deleted.
    """
    await cursor.execute(
        """
        DELETE FROM NotionTask
        WHERE ID = ?
        """,
        (task_id,),
    )

    # Commit the changes to the database
    await conn.commit()
    logging.info(f"Notion task with ID {task_id} deleted.")


async def delete_relation_row(id):
    """
    Deletes a relation row based on the provided notion/todoist task id.
    """
    await cursor.execute(
        """
        DELETE FROM Relation
        Where TodoistTaskID = ? or NotionTaskID = ?
        """,
        (
            str(id),
            str(id),
        ),
    )
    await conn.commit()
