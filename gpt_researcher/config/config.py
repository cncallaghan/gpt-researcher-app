# config file
import json
import threading
from mylogger import LoggerSingleton

logger = LoggerSingleton()


class Config:
    """Config class for GPT Researcher."""

    __instance = None
    __lock = threading.Lock()

    def __new__(cls, config_file: str = None):
        if cls.__instance is None:
            with cls.__lock:  # auto aquire and release lock
                if cls.__instance is None:
                    cls.__instance = super(Config, cls).__new__(cls)
                    cls.__init_variables(cls, config_file)
                    logger.log_debug("config.py - Config file created")

        logger.log_debug("config.py - Config file returned")
        return cls.__instance

    def __init_variables(self, config_file: str = None):
        """Initialize the config class."""
        self.config_file = config_file
        self.retriever = "tavily"
        self.llm_provider = "ChatOpenAI"
        self.fast_llm_model = "gpt-3.5-turbo-16k"
        self.smart_llm_model = "gpt-4-1106-preview"
        self.fast_token_limit = 2000
        self.smart_token_limit = 4000
        self.browse_chunk_max_length = 8192
        self.summary_token_limit = 700
        self.temperature = 0.6
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        )
        self.memory_backend = "local"
        self.total_words = 1000
        self.report_format = "apa"
        self.max_iterations = 3

        self.load_config_file(self)

    def load_config_file(self) -> None:
        """Load the config file."""
        if self.config_file is None:
            return None
        with open(self.config_file, "r") as f:
            config = json.load(f)
        for key, value in config.items():
            self.__dict__[key] = value

    def update_temperature(self, new_temperature: float) -> None:
        self.temperature = new_temperature
        logger.log_debug("config.py - Temperature updated: %s", self.temperature)
