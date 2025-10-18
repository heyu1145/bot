class BotException(Exception):
    pass

class TokenException(BotException):
    pass

class TokenNoFoundError(TokenException):
    pass

class WrongTokenError(TokenException):
    pass

class OwnerUseridException(BotException):
    pass

class OwnerUseridNoFoundError(OwnerUseridException):
    pass

