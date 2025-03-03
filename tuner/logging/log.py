"""
Tuner log
"""

import os
import sys
import time
import inspect
from loguru import logger
from tuner.config import LogConfig

stack_t = inspect.stack()
ins = inspect.getframeinfo(stack_t[1][0])
exec_dir = os.path.dirname(os.path.abspath(ins.filename))
report_dir = os.path.join(exec_dir, "reports")
if os.path.exists(report_dir) is False:
    os.mkdir(report_dir)

with open(os.path.join(report_dir, "tuner_log.log"), "w") as log:
    log.truncate(0)

if LogConfig.LOG_PATH is None:
    LogConfig.LOG_PATH = os.path.join(report_dir, "tuner_log.log")


class LogConfigSetter:
    """log config"""

    def __init__(self, level: str = "DEBUG", colorlog: bool = True):
        self.logger = logger
        self._colorlog = colorlog
        self._console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</> <level>| {level: <8} | {file} | {thread.name} | {message}</level>"
        self._log_format = "{time: YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | {file: <10} | {thread.name} | {message}"
        self._level = level
        self.logfile = LogConfig.LOG_PATH
        self.set_level(self._colorlog, self._console_format, self._level)
        self.file_stream_handler_id = None

    def set_level(
        self, colorlog: bool = True, format: str = None, level: str = "DEBUG"
    ):
        """
        setting level
        :param colorlog:
        :param format:
        :param level:
        :return:
        """
        if format is None:
            format = self._console_format
        self.logger.remove()
        self._level = level
        self.logger.add(sys.stderr, level=level, colorize=colorlog, format=format)
        self.file_stream_handler_id = self.logger.add(
            self.logfile,
            level=level,
            colorize=False,
            format=self._log_format,
            encoding="utf-8",
        )

    def set_logger_file_path(self, path: str, format: str = None, level: str = "DEBUG"):
        if format is None:
            format = self._console_format
        self.logger.remove()
        self._level = level
        # 将logger的第二个handler的文件路径修改为path
        self.logger.remove(self.file_stream_handler_id)
        self.file_stream_handler_id = self.logger.add(
            path,
            level=level,
            colorize=False,
            format=self._log_format,
            encoding="utf-8",
        )


# log level: TRACE < DEBUG < INFO < SUCCESS < WARNING < ERROR
log_cfg = LogConfigSetter(level="TRACE")
log = logger
