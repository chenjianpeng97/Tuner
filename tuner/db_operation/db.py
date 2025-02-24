"""
SQL API
"""

from sqlalchemy import create_engine
from sqlalchemy.sql import text


class DataBase:
    """SQL base API"""

    def __init__(self, url: str):
        self.url = url
        self.engine = create_engine(url)
        self.conn = None

    def execute(self, sql: str):
        """
        excute sql statement
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return result.fetchall()

    def execute_file(self, file_name: str, params: dict = None):
        """
        excute sql file or excute sql file with params(:params as placeholder in *.sql file)
        """
        with self.engine.connect() as conn:
            self.conn = conn
            with open(file_name, "r") as file:
                sql = file.read()
                self.conn.execute(text(sql), params)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
