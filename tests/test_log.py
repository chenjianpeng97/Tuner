import pytest
from tuner.logging import log, log_cfg
from tuner.utils import file
from tuner.config import LogConfig


class TestLog:
    def test_log(self):
        # 测试结果放在test目录下的testresult中
        TESTRESULT_DIR = file.dir
        log.info(TESTRESULT_DIR)
        log_cfg.set_logger_file_path(file.join(file.dir, "testresult", "log_test.log"))
        log.trace("A trace message.")
        log.debug("A debug message.")
        log.info("An info message.")
        log.success("A success message.")
        log.warning("A warning message.")
        log.error("An error message.")
        log.critical("A critical message.")
