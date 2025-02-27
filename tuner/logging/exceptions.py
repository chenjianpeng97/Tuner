"""
Exceptions that may happen in all the tuner code.
"""


class TunerException(Exception):
    """
    Base tuner exception.
    """

    def __init__(self, msg: str = None, screen: str = None, stacktrace: str = None):
        self.msg = msg
        # 异常时截图
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = f"Message: {self.msg}\n"
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += f"Stacktrace:\n{stacktrace}"
        return exception_msg


class SQLFileError(TunerException):
    """
    输入了不支持的sql文件内容
    """

    pass


class DBConnectionError(TunerException):
    """
    数据库连接错误
    """

    pass
