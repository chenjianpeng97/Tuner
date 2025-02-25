import os
import pytest
from sqlalchemy import create_engine, text
from tuner.db_operation.db import DataBase
from tuner.utils import file, retry
import sys

TESTDATA_DIR = file.join(file.dir, "testdata")


@retry(delay_seconds=5, max_tries=6)
def clean_dbfile(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("test.db has been deleted.")
    else:
        print("test.db does not exist.")


@retry(delay_seconds=5, max_tries=6)
def drop_all_tables(db: DataBase):
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables:
        db.execute(text(f"DROP TABLE IF EXISTS {table['name']}"))
    db.commit()


@pytest.fixture(scope="function")
def db():
    # 清理sqlite数据库
    clean_dbfile(file.join(TESTDATA_DIR, "test.db"))
    # 创建一个 SQLite 数据库
    db_url = "sqlite:///" + TESTDATA_DIR + "/test.db"
    db = DataBase(db_url)
    yield db
    db.close()
    # 显式断开连接并释放资源
    db.engine.dispose()
    clean_dbfile(file.join(TESTDATA_DIR, "test.db"))

class TestDB:

    def test_execute_file(self, db):
        # 创建users表
        db.execute_file(file.join(TESTDATA_DIR, "create_table.sql"))
        params = {"name": "Alice", "age": 25}
        r = db.execute_file(file.join(TESTDATA_DIR, "sql_with_params.sql"), params)
        assert r == 1
        result = db.execute("SELECT * FROM users WHERE name = 'Alice';")[0]
        print("result ====== ")
        print(result)
        assert result == (1, "Alice", 25)

    def test_execute_statement_create_table_return_if_success(self, db):
        sql = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);"
        result1 = db.execute(sql)
        assert result1 == True
        # 再次执行，创建表会失败，因已有同名表
        result2 = db.execute(sql)
        assert result2 == False

    def test_execute_statement_select_return_fetchall(self, db):
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);"
        )
        db.execute("INSERT INTO users (name, age) VALUES ('Alice', 25);")
        db.execute("INSERT INTO users (name, age) VALUES ('Bob', 30);")
        result = db.execute("SELECT * FROM users;")
        assert result == [(1, "Alice", 25), (2, "Bob", 30)]

    def test_execute_statement_insert_update_delete_return_affected_rowcount(self, db):
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);"
        )
        result1 = db.execute(
            "INSERT INTO users (name, age) VALUES ('Alice', 25), ('Bob', 30);"
        )
        assert result1 == 2
