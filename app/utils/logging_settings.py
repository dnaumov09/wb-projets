import logging
from colorama import Fore, Style, init

LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

MESSAGE_FORMAT = '[%(levelname)s] %(asctime)-30s:  %(message)s'
DATE_FORMAT = '%d-%m-%Y %H:%M:%S'

class Formatter(logging.Formatter):
    def format(self, record):
        timestamp = self.formatTime(record, self.datefmt)
        color = self.LEVEL_COLORS.get(record.levelno, "")
        levelname = f"[{record.levelname}]"
        return f"{color}{levelname:<10} {timestamp}:    {record.getMessage()}{Style.RESET_ALL}"


def set_loggers_level(level):
    logging.getLogger(__name__).setLevel(level)
    
    # for not main loggers
    if level < logging.WARNING:
        level = logging.WARNING    
    logging.getLogger('httpx').setLevel(level)
    logging.getLogger('telegram').setLevel(level)


def init_logging(level: int = logging.INFO):
    init(autoreset=True)
    set_loggers_level(level)

    handler = logging.StreamHandler()
    handler.setFormatter(Formatter(fmt=MESSAGE_FORMAT,datefmt='%d-%m-%Y %H:%M:%S'))
    
    logger = logging.getLogger()
    logger.addHandler(handler)


    
