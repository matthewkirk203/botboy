import logging

def setup_logger():
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt_str)

        if False:
            log_path = 'logs/botlogs.log'
            fh = logging.FileHandler(log_path)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)

        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)

        logger.addHandler(sh)
        logger.addHandler(fh)