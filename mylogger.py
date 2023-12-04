import logging
import threading


class LoggerSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, log_file="app.log", level=logging.DEBUG):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerSingleton, cls).__new__(cls)
                cls._instance._setup_logger(log_file, level)
        return cls._instance

    def _setup_logger(self, log_file, level):
        logging.basicConfig(
            filename=log_file,
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def log_debug(self, *args):
        self.logger.debug(*args)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_critical(self, message):
        self.logger.critical(message)
