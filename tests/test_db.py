import os
import pytest
from sqlalchemy import create_engine, text
import tuner
from tuner.db_operation.db import DataBase
from tuner.utils import file

TESTDATA_DIR = file.join(file.dir, "testdata")
class TestDB:
    def __init__(self):
        self.db_url = "sqlite:///" + TESTDATA_DIR + "/test.db"
        self.db = DataBase(self.db_url)
        self.setup_db()

    def setup_db(self):
        with self.db.engine.connect() as conn:
            conn.execute(
                text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);")
            )
            conn.execute(text('INSERT INTO users (name, age) VALUES ("Alice", 25);'))
            conn.execute(text('INSERT INTO users (name, age) VALUES ("Bob", 30);'))

    def test_execute_file(self):
        params = {"name": "Alice"}
        self.db.execute_file(file.join(TESTDATA_DIR,"test_db.sql"), params)
        with self.db.engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM users WHERE name = :name"), params
            ).fetchone()
            assert result is not None
            assert result["name"] == "Alice"
            assert result["age"] == 25