"""
load config from imported dir (default . ),
load token from .env file
"""

from sys import getdefaultencoding
import json
from pathlib import Path
import dotenv
from utils.logger import get_logger

charset = getdefaultencoding()
logger, *_ = get_logger(__name__)

default = {"prefix": "!"}

this_dir: Path = Path(__file__).parent


class ConfigLoader:
    def __init__(self, config_dir: Path | str = this_dir) -> None:
        self.config_dir: Path = Path(config_dir)
        if not self.config_dir.is_dir():
            logger.critical("Config directory %s does not exist", self.config_dir)
            raise NotADirectoryError(f"{self.config_dir} is not a valid directory")
        self.config: dict = {}

    def load_config(
        self, config_filename: str = "config.json", encoding: str = charset
    ) -> dict:
        config_path = self.config_dir / config_filename

        if not config_path.exists():
            logger.warning(
                "Config file %s does not exist, creating default", config_path
            )
            with open(config_path, "w", encoding=encoding) as config_file:
                json.dump(default, config_file, indent=4)

        if not config_path.is_file():
            logger.critical("Config path %s is not a file", config_path)
            raise FileNotFoundError(f"{config_path} is not a valid file")

        try:
            with open(config_path, "r", encoding=encoding) as config_file:
                self.config = json.load(config_file)
            logger.debug("Loaded config from %s", config_path)
        except Exception as e:
            logger.exception("Failed to load config from %s: %s", config_path, e)
            raise RuntimeError("Failed to load config") from e
        return self.config

    def load_token(self, token_key: str = "TOKEN") -> str:
        dotenv_pathstr = dotenv.find_dotenv()

        if dotenv_pathstr == "":
            logger.error("No .env file found in %s or parent directories", self.config_dir)
            raise FileNotFoundError("No .env file found, please copy .env.example to .env and set your token")

        dotenv_path = Path(dotenv_pathstr)

        token = dotenv.get_key(dotenv_path, token_key, encoding=charset)

        if token:
            logger.debug("Loaded token from file %s", dotenv_path)
        else:
            logger.critical("Failed to load token")
            raise RuntimeError(
                f"Failed to load token, please set the token in the .env file with the key {token_key}"
            )
        return token
