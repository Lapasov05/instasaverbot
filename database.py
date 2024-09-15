import sqlite3

def con():
    return sqlite3.connect('instasaver.db')


def create_table_user():
    try:
        conn = con()
        cur = conn.cursor()

        # Create the users table if it doesn't exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(30),
            chat_id VARCHAR(150),
            user_id VARCHAR(150),
            role_id INTEGER DEFAULT 1,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create the statistics table if it doesn't exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instagram INTEGER DEFAULT 0,
            tiktok INTEGER DEFAULT 0,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            shortcode TEXT UNIQUE
        )
        """)

        # Check if a row with id = 1 already exists
        cur.execute("SELECT id FROM statistics WHERE id = 1")
        if cur.fetchone() is None:
            # Insert the initial row if it doesn't exist
            cur.execute("""
            INSERT INTO statistics (instagram, tiktok) 
            VALUES (0, 0)
            """)

        conn.commit()
        print("Tables created")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

    finally:
        conn.close()


def insert_data(data: dict):
    try:
        conn = con()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO users (username, chat_id, user_id)
        VALUES (?, ?, ?)
        """, (data['username'], data['chat_id'], data['user_id']))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()

def update_statistics(platform: str):
    try:
        conn = con()
        cur = conn.cursor()
        if platform == 'instagram':
            cur.execute("UPDATE statistics SET instagram = instagram + 1 WHERE id = 1")
        elif platform == 'tiktok':
            cur.execute("UPDATE statistics SET tiktok = tiktok + 1 WHERE id = 1")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating statistics: {e}")
    finally:
        conn.close()

def check_chat_id_exists(chat_id):
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE chat_id = ?", (str(chat_id),))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def get_user_role(chat_id):
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT role_id FROM users WHERE chat_id = ?", (str(chat_id),))
    role = cur.fetchone()
    conn.close()
    return role[0] if role else None

def get_statistics():
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT instagram, tiktok FROM statistics WHERE id = 1")
    result = cur.fetchone()
    conn.close()
    return result if result else (0, 0)

def get_all_users():
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT username, user_id, chat_id, role_id, created_date FROM users")
    users = cur.fetchall()
    conn.close()

    # Convert tuples to dictionaries
    return [
        {
            'username': user[0],
            'user_id': user[1],
            'chat_id': user[2],
            'role_id': user[3],
            'created_date': user[4]
        }
        for user in users
    ]
def update_user_roles(user_ids):
    try:
        conn = con()
        cur = conn.cursor()
        cur.executemany(
            "UPDATE users SET role_id = 2 WHERE user_id = ?",
            [(user_id,) for user_id in user_ids]
        )
        conn.commit()
        print(f"Updated roles for user_ids: {user_ids}")
    except sqlite3.Error as e:
        print(f"Error updating user roles: {e}")
    finally:
        conn.close()


def add_video(file_id, shortcode):
    try:
        conn = con()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO videos (file_id, shortcode)
        VALUES (?, ?)
        """, (file_id, shortcode))

        # Commit the transaction
        conn.commit()
        print("Video added successfully!")

    except sqlite3.IntegrityError:
        print("Error: The shortcode must be unique.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Check if the shortcode exists and return the file_id if it does
def check_shortcode_exists(shortcode):
    conn = con()
    cur = conn.cursor()
    cur.execute("""
    SELECT file_id FROM videos WHERE shortcode = ?
    """, (shortcode,))

    result = cur.fetchone()

    if result:
        return result[0]  # Return file_id if shortcode exists
    else:
        return None  # Shortcode does not exist

# List of user_ids to be updated
user_ids_to_update = ['7105920111', '468374402']
update_user_roles(user_ids_to_update)
# Example usage:
create_table_user()


