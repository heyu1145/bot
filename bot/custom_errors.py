"""
custom errors from bot
"""


class BotException(Exception):
    """Base class for bot exceptions."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ConfigLoadError(BotException):
    """Exception raised for errors in loading configuration."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CogLoadError(BotException):
    """Exception raised for errors in loading cogs."""

    def __init__(self, cog_name: str, message: str):
        self.cog_name = cog_name
        self.message = message
        super().__init__(f"Error loading cog {self.cog_name}: {self.message}")


class TokenLoadError(BotException):
    """Exception raised for errors in loading token."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidConfigError(BotException):
    """Exception raised for invalid configuration values."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MissingTokenError(BotException):
    """Exception raised when the token is missing."""

    def __init__(self):
        super().__init__("Token is missing from the environment variables.")


class InvalidTokenError(BotException):
    """Exception raised when the token is invalid."""

    def __init__(self):
        super().__init__("The provided token is invalid.")


class CogLoadTimeoutError(BotException):
    """Exception raised when loading a cog times out."""

    def __init__(self, cog_name: str):
        self.cog_name = cog_name
        super().__init__(f"Loading cog {self.cog_name} timed out.")


class ConfigFileNotFoundError(BotException):
    """Exception raised when the configuration file is not found."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        super().__init__(f"Configuration file not found: {self.config_path}")
