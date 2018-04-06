import logging

def setup_logger():
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        fmt_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt_str)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)

        logger.addHandler(sh)