import psycopg2
from psycopg2 import sql
from config import DB_PORT, DB_HOST, DB_PASSWORD, DB_NAME, DB_USER

def con():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_table_user():
    try:
        with con() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(30),
                    chat_id VARCHAR(150),
                    user_id VARCHAR(150),
                    role_id INTEGER DEFAULT 1,
                    created_date TIMESTAMP DEFAULT current_timestamp
                )
                """)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id SERIAL PRIMARY KEY,
                    instagram INTEGER DEFAULT 0,
                    tiktok INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT current_timestamp
                )
                """)
                conn.commit()
                print("Tables created")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()

def insert_data(data: dict):
    try:
        with con() as conn:
            with conn.cursor() as cur:
                insert_query = sql.SQL("""
                INSERT INTO users(username, chat_id,user_id)
                VALUES (%s, %s,%s)
                """)
                cur.execute(insert_query, (data['username'], data['chat_id'],data['user_id']))
                conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()



def update_statistics(platform: str):
    conn = con()
    cur = conn.cursor()
    if platform == 'instagram':
        cur.execute("UPDATE statistics SET instagram = instagram + 1 WHERE id = 1")
    elif platform == 'tiktok':
        cur.execute("UPDATE statistics SET tiktok = tiktok + 1 WHERE id = 1")
    conn.commit()
    conn.close()


def check_chat_id_exists(chat_id):
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE chat_id = %s", (str(chat_id),))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def get_user_role(chat_id):
    conn = con()
    cur = conn.cursor()
    cur.execute("SELECT role_id FROM users WHERE chat_id = %s", (str(chat_id),))
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


# Example usage:
create_table_user()
