import logging

logger = logging.getLogger("server-log")
if not logger.hasHandlers():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    fh = logging.FileHandler(filename="server-log.log", mode="w")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
