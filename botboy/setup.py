import os
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler

# Make logs directory if it doesn't exist
def make_log_dir():
    logs_dir = os.path.dirname(os.path.realpath(__file__)) + "/logs"
    if not os.path.isdir(logs_dir):
        os.makedirs(logs_dir)

# Setup logging
def setup_logger():
    make_log_dir()
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt_str)

        # Streaming logs to the console
        if False:
            sh = logging.StreamHandler()
            sh.setLevel(logging.INFO)
            sh.setFormatter(formatter)
            logger.addHandler(sh)

        # Logging to file (rotating with max size of 100 MB)
        if True:
            log_path = 'logs/botlogs.log'
            fh = RotatingFileHandler(log_path, maxBytes=100000000, backupCount=4)
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        # Logging to file (rotating with max size of 100 MB)
        if True:
            log_path = 'logs/debug_botlogs.log'
            fh_debug = RotatingFileHandler(log_path, maxBytes=100000000, backupCount=1)
            fh_debug.setLevel(logging.DEBUG)
            fh_debug.setFormatter(formatter)
            logger.addHandler(fh_debug)

