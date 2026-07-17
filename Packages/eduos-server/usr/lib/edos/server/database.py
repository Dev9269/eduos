import sqlite3
import os

DB_PATH = "/var/lib/edos/server.db"


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get("EDOS_DB_PATH") or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'student',
                active INTEGER DEFAULT 1,
                created TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                code TEXT UNIQUE,
                created TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                course_id INTEGER,
                duration_min INTEGER DEFAULT 60,
                status TEXT DEFAULT 'draft',
                questions TEXT DEFAULT '[]',
                created TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER,
                user_id INTEGER,
                answers TEXT,
                score REAL,
                submitted TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(exam_id) REFERENCES exams(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)
        self.conn.commit()

    def query(self, sql, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()

    def execute(self, sql, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        if self.conn:
            self.conn.close()
