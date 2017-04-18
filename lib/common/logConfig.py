import logging


def get_logger(name, enable_advance=None):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if enable_advance:
        logger.setLevel(logging.DEBUG)
        return logger
    logger.setLevel(logging.INFO)
    return logger
