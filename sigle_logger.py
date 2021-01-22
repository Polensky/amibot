"""
Custom logger
"""
import logging # pylint: disable=no-absolute-import
from datetime import datetime

def start_logger():
    """
    Start custom logger
    """
    logger = logging.getLogger(__name__)

    date = datetime.now()
    date_str = date.strftime('%d-%b-%Y')

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(f'logging/amibot_{date_str}.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.WARNING)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    logger.info('Logger online!')
