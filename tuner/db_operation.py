"""
SQL API
执行sql语句
执行sql文件
执行带参sql语句
执行带参sql文件
"""

import sqlparse
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os
from typing import Union
from tuner.exceptions import SQLFileError, DBConnectionError


class DataBase:
    """SQL base API"""

    def __init__(self, url: str):
        if not url:
            raise DBConnectionError("Please provide a valid database url in config.py.")
        self.url = url
        self.engine = create_engine(url)
        self.conn = None

    def execute(self, sql: str, params: dict = None) -> Union[int, bool, list]:
        """
        execute sql statement
        """
        with self.engine.connect() as conn:
            try:
                result = conn.execute(text(sql), params)
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

    def execute_file(self, file_name: str, params: dict = None) -> list:
        """
        excute sql file or excute sql file with params(:params as placeholder in *.sql file)
        ilgal input:
            1. multiple sql statements with params
        legal input:
            1. single sql statement without params
            2. single sql statement with params
            3. multiple sql statements without params
        """
        results = []
        # 检查sql file合法性
        if not os.path.isfile(file_name):
            raise SQLFileError(f"SQL file {file_name} does not exist.")

        with open(file_name, "r", encoding="utf-8") as file:
            sql = file.read()
            statements = sqlparse.split(sql)
            for statement in statements:
                if statement.strip():
                    if params:
                        result = self.execute(sql=str(statement), params=params)
                        results.append(result)
                    else:
                        result = self.execute(sql=str(statement))
                        results.append(result)
            return results

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
