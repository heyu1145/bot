class BotException(Exception):
    pass

class TokenException(BotException):
    pass

class TokenNotFoundError(TokenException):
    pass

class TokenNoFoundError(TokenException):  # Kept for backward compatibility
    pass

class WrongTokenError(TokenException):
    pass

class OwnerUseridException(BotException):
    pass

class OwnerUseridNoFoundError(OwnerUseridException):
    pass

class BasicFileNotFoundError(BotException):
    pass

class BotStartFailure(BotException):
    pass

