class HostIsNotReachableError(Exception):
    pass

class InvalidCredentialError(Exception):
    pass


class NoMemberFoundError(Exception):
    pass


class UnknownCommandActionError(Exception):
    pass


class InsufficientArgumentError(Exception):
    pass


class CommandNotFoundError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass

class UnsupportedCommand(Exception):
    pass