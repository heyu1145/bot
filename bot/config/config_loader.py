"""
load config from imported dir (default . ),
load token from .env file
"""
import os
from sys import getdefaultencoding
from pathlib import Path
from dotenv import load_dotenv
import json
from utils.logger import get_logger
from custom_errors import ConfigLoadError, MissingTokenError

charset = getdefaultencoding()
logger, *_ = get_logger(__name__)

default = {"prefix": "!"}

default_dir: str = Path(__file__).parent.name


class ConfigLoader:
    def __init__(self, config_dir: str = default_dir) -> None:
        self.config_dir: str = config_dir
        self.config: dict = {}

    def load_config(self, config_filename: str = "config.json", encoding: str = charset) -> dict:
        config_path = Path(self.config_dir) / config_filename

        try:
            with open(config_path, 'r', encoding=encoding) as config_file:
                self.config = json.load(config_file)
            logger.info("Loaded config from %s", config_path)
        except FileNotFoundError:
            logger.warning(
                f"Config file not found at %s, default %s", config_path, default)
            with open(config_path, 'w', encoding=encoding) as config_file:
                json.dump(default, config_file)
        except Exception as e:
            logger.exception("Failed to load config from %s: %s",
                             config_path, e)
            raise ConfigLoadError(f"Could not load config: {e}")
        return self.config

    def load_token(self, token_key: str = "TOKEN") -> str:
        load_dotenv()
        token = os.getenv(token_key)
        if token:
            logger.info("Loaded token")
        else:
            logger.critical("Failed to load token")
            raise MissingTokenError
        return token
