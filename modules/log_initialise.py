import logging
import os
from datetime import datetime

 
# logger will take a filename and a directory as inputs

def setup_logger(timestamp:str, logDir:str, debug = False):
    """_summary_

    Args:
        timestamp (str): the timestamp will be the log filename
        logDir (str): folder name to save logs to

    Returns:
        logging.logger: logger object
    """

    os.makedirs(logDir, exist_ok = True)

    logFilename = f'{logDir}/{timestamp}_{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.log'

    logging.basicConfig(
        filename = logFilename,
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level = logging.INFO if debug == False else logging.DEBUG
    )
    return logging.getLogger()