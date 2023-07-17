import logging
from jarvis.jarvis import Jarvis
from config import const

logger = logging.getLogger()

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)-15s] [%(funcName)s()][%(levelname)s] %(message)s')
    logger.setLevel(const.LOG_LEVEL)

    j = Jarvis.load(logger)
    j.start()
