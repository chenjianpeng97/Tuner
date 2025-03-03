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

__all__ = [
    "ClassNotFoundError",
    "ConfigError",
    "ConfigTypeError",
    "ConstraintError",
    "FileNotFoundError",
    "InvalidClassError",
    "InvalidFileLocationError",
    "InvalidFilenameError",
    "ModuleNotFoundError",
    "NotSupportedWarning",
    "ObjectNotFoundError",
    "ResourceExistsError",
    "TagExpressionError",
]


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES:
# ---------------------------------------------------------------------------
class ConstraintError(RuntimeError):
    """
    Used if a constraint/precondition is not fulfilled at runtime.

    .. versionadded:: 1.2.7
    """

class ResourceExistsError(ConstraintError):
    """
    Used if you try to register a resource and another exists already
    with the same name.

    .. versionadded:: 1.2.7
    """

class ConfigError(Exception):
    """Used if the configuration is (partially) invalid."""

class ConfigParamTypeError(ConfigError):
    """Used if a config-param has the wrong type."""


# ---------------------------------------------------------------------------
# EXCEPTION/ERROR CLASSES: Related to aoloader
# ---------------------------------------------------------------------------
class FileNotFoundError(NotImplementedError):
    """Should be raised if a *.py file is not implemented yet."""

