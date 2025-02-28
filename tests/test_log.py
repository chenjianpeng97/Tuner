import pytest
from tuner.logging.log import set_logger
from tuner.utils import file

TESTRESULT_DIR = file.join(file.dir, "testresult")


@pytest.fixture(scope="module")
def logger():
    # 初始化logger
    logger = set_logger(file.join(TESTRESULT_DIR, "tuner_log.log"))
    yield logger


class TestLogger:
    def test_logger(self, logger):
        logger.trace("A trace message.")
        logger.debug("A debug message.")
        logger.info("An info message.")
        logger.success("A success message.")
        logger.warning("A warning message.")
        logger.error("An error message.")
        logger.critical("A critical message.")
