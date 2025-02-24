import pymysql
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config import DB_CONFIG,BASE_DIR

# 默认放testdata的目录在根目录的./testdata下
DEFAULT_TESTDATA_DIR = os.path.join(BASE_DIR, "testdata")
class MySQL:
    def __init__(self):
        self.connection = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def query(self, sql, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
        return result

    def execute(self, sql, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            self.connection.commit()

    def close(self):
        self.connection.close()

    # 执行sql文件
    def excute_sqlfile(self, file_name: str):
        """
        作为文件对外的接口 执行sql语句以初始化测试数据
        """
        with open(os.path.join(DEFAULT_TESTDATA_DIR,file_name), "r", encoding="utf-8") as f:
            sqls = f.read().split(";")
            for sql in sqls:
                if sql.strip():
                    self.execute(sql)


# Example usage
if __name__ == "__main__":
    db = MySQL()
    try:
        # Example query
        result = db.query("SELECT * FROM supplier_data")
        print(result)

        # Example insert
        # db.execute("INSERT INTO your_table_name (column1, column2) VALUES (%s, %s)", ('value1', 'value2'))
        # Example excute_sqlfile
        db.excute_sqlfile("授权前置条件.sql")
    finally:
        db.close()
