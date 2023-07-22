import logging
from config import const
from loader.loader import load

logger = logging.getLogger()

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)-15s] [%(funcName)s()][%(levelname)s] %(message)s')
    logger.setLevel(const.LOG_LEVEL)

    j = load(logger)
    j.start()
