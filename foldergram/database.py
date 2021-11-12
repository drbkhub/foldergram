import sqlite3
import sys, os

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    # print(f'{sys.executable=}')
elif __file__:
    application_path = os.path.dirname(__file__)


DATABASE_NAME = 'database.db'

sql_create_table = """
CREATE TABLE IF NOT EXISTS users(
	user_id INTEGER PRIMARY KEY
);
"""

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect(os.path.join(application_path, DATABASE_NAME))
con.row_factory = dict_factory
cur = con.cursor()
cur.executescript(sql_create_table)


def add_user(user_id):
    cur.execute("""
    INSERT OR IGNORE INTO users(user_id) VALUES(?);
    """, (int(user_id),))
    con.commit()

def all_users():
    cur.execute("""
    SELECT user_id FROM users;
    """)
    return cur.fetchall()