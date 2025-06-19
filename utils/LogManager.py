import os
import logging
from datetime import datetime


class LogManager:
    _instance = None
    _logger = None
    _log_file = None

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls._configure_logging()
        return cls._logger

    @classmethod
    def get_log_file(cls):
        if cls._log_file is None:
            cls._configure_logging()
        return cls._log_file

    @classmethod
    def _configure_logging(cls):
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            cls._log_file = os.path.join(log_dir, f'file_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

            logging.basicConfig(level=logging.DEBUG, 
                              format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', 
                              handlers=[logging.FileHandler(cls._log_file), logging.StreamHandler()])

            cls._logger = logging.getLogger('FileManager')
            cls._logger.info("Sistema de logging configurado com sucesso")

        except PermissionError:
            user_data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'File-Folder-Manager', 'logs')
            os.makedirs(user_data_dir, exist_ok=True)
            cls._log_file = os.path.join(user_data_dir, f'file_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

            logging.basicConfig(level=logging.DEBUG, 
                              format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', 
                              handlers=[logging.FileHandler(cls._log_file), logging.StreamHandler()])

            cls._logger = logging.getLogger('FileManager')
            cls._logger.info(f"Sistema de logging configurado com diretório alternativo: {user_data_dir}")

    @classmethod
    def debug(cls, message):
        cls.get_logger().debug(message)

    @classmethod
    def info(cls, message):
        cls.get_logger().info(message)

    @classmethod
    def warning(cls, message):
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message, exc_info=False):
        cls.get_logger().error(message, exc_info=exc_info)

    @classmethod
    def critical(cls, message, exc_info=True):
        cls.get_logger().critical(message, exc_info=exc_info)
