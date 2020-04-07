class RootException(Exception):
    pass


class CollectorError(RootException):
    pass


class NoIdsError(CollectorError):
    pass
