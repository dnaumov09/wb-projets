import logging
from colorlog import ColoredFormatter

TEXT_FORMAT = "%(log_color)s[%(levelname)s] %(asctime)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_COLORS = {
    # 'DEBUG':    'cyan',
    # 'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'bold_red',
    }

formatter = ColoredFormatter(
    fmt=TEXT_FORMAT,
    datefmt=DATE_FORMAT,
    log_colors=LOG_COLORS
)

def init_logging(level: int = logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.getLogger('httpx').setLevel(level=logging.WARNING if level < logging.WARNING else level)
    logging.getLogger('telegram').setLevel(level=logging.WARNING if level < logging.WARNING else level)
