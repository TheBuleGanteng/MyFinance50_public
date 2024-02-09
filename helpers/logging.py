import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

def setup_logging(app: Flask):
    # Set up logging to file
    if app.config.get('LOG_TO_FILE', False):
        file_handler = RotatingFileHandler(app.config.get('LOG_FILE_PATH'), maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        app.logger.addHandler(file_handler)

    # Set up logging to console
    if app.config.get('LOG_TO_CONSOLE', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)