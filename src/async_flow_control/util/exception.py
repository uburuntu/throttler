
class ThrottlerInvArg(ValueError):
    """
    An invalid argument passed to a throttler constructor
    """
    pass

class ThrottlerException(RuntimeError):
    """
    An exception generated during throttler scheduling
    """
    pass


class LimitExceeded(ThrottlerException):
    """
    A runtime limit was exceeded
    """
    pass

class QueueSizeExceeded(LimitExceeded):
    pass

class WaitTimeExceeded(LimitExceeded):
    pass

class ThrottlerTimeout(LimitExceeded):
    pass
