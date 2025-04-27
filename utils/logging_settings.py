import logging

def init_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger('httpx').setLevel(level=logging.WARNING if level < logging.WARNING else level)
    logging.getLogger('telegram').setLevel(level=logging.WARNING if level < logging.WARNING else level)
