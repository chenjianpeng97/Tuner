"""
SQL API
"""

from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os
from typing import Union


class DataBase:
    """SQL base API"""

    def __init__(self, url: str):
        self.url = url
        self.engine = create_engine(url)
        self.conn = None

    def execute(self, sql: str) -> Union[int, bool, list]:
        """
        execute sql statement
        """
        with self.engine.connect() as conn:
            try:
                result = conn.execute(text(sql))
            except Exception as e:
                print(f"An error occurred: {e}")
                return False
            # 查询语句fetchall()返回查询结果，增删改语句返回影响行数
            if sql.strip().lower().startswith("select"):
                return result.fetchall()
            elif sql.strip().lower().startswith(("insert", "update", "delete")):
                conn.commit()
                return result.rowcount
            else:
                conn.commit()
                return True

    def execute_file(self, file_name: str, params: dict = None) -> bool:
        """
        excute sql file or excute sql file with params(:params as placeholder in *.sql file)
        """
        try:
            with self.engine.connect() as conn:
                self.conn = conn
                with open(file_name, "r") as file:
                    sql = file.read()
                    self.conn.execute(text(sql), params)
                    self.conn.commit()
                    return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()


if __name__ == "__main__":
    if os.path.exists("test_db.sqlite"):
        os.remove("test_db.sqlite")
        print("test_db.sqlite has been deleted.")
    else:
        print("The file does not exist.")
    db = DataBase("sqlite:///test_db.sqlite")
    print(
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);"
        )
    )
    print(db.execute("SELECT * FROM users;"))
    print(db.execute("INSERT INTO users (name, age) VALUES ('Alice', 25);"))
    print(
        db.execute(
            "INSERT INTO users (name, age) VALUES " "('Bob', 30), " "('Charlie', 22);"
        )
    )
    print(db.execute("SELECT * FROM users;"))
    db.close()
