import logging
from colorama import Fore, Style, init

init(autoreset=True, strip=False, convert=False)

MESSAGE_FORMAT = '[%(levelname)s] %(asctime)-30s:  %(message)s'
DATE_FORMAT = '%d-%m-%y %H:%M:%S'

class Formatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.LIGHTCYAN_EX,
        logging.INFO: Fore.LIGHTGREEN_EX,
        logging.WARNING: Fore.LIGHTYELLOW_EX,
        logging.ERROR: Fore.LIGHTRED_EX,
        logging.CRITICAL: Fore.LIGHTRED_EX + Style.BRIGHT
    }

    def format(self, record):
        timestamp = self.formatTime(record, self.datefmt)
        if record.levelname == 'INFO':
            message = f"{Style.RESET_ALL}{timestamp}:    {record.getMessage()}"
        else: 
            message = f"{timestamp}:    {record.getMessage()}{Style.RESET_ALL}"

        color = self.LEVEL_COLORS.get(record.levelno, "")
        levelname = f"[{record.levelname}]"
        return f"{color}{levelname:<10} {message}"
    
formatter = Formatter(fmt=MESSAGE_FORMAT,datefmt='%d-%m-%Y %H:%M:%S')


def set_orher_loggers_level(level):
    # for not main loggers
    if level < logging.WARNING:
        level = logging.WARNING    
    logging.getLogger('httpx').setLevel(level)
    logging.getLogger('telegram').setLevel(level)
    logging.getLogger("apscheduler").setLevel(level)


def init_logging(level: int = logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)

    set_orher_loggers_level(level)


def get_uvicorn_log_config():
    level = logging.getLogger().getEffectiveLevel()
    level = logging.getLevelName(level)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "custom": {
                "()": formatter.__class__,
                "fmt": formatter._fmt,
                "datefmt": formatter.datefmt,
            }
        },
        "handlers": {
            "default": {
                "formatter": "custom",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": level, "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": level, "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": level, "propagate": False},
        },
        "root": {"level": level, "handlers": ["default"]},
    }