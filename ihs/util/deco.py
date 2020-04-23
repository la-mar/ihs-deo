import functools
import logging

logger = logging.getLogger(__name__)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def safe_convert(func):
    """ Generic error handling decorator for primative type casts """

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.debug(f"{func} failed: {e}")
            return None

    return func_wrapper
