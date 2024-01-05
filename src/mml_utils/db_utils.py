import sqlite3


class Cursor:

    def __init__(self, conn: sqlite3.Connection, commit=True):
        self.conn = conn
        self.commit = commit

    def __enter__(self):
        self.cur: sqlite3.Cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        if self.commit:
            self.conn.commit()

    def execute(self, *args, **kwargs):
        return self.cur.execute(*args, **kwargs)
