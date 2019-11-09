import time
from functools import wraps
import urllib.parse
import os


def from_file(filename: str) -> str:
    xml = None
    with open(filename, "r") as f:
        xml = f.read().splitlines()
    return "".join(xml)


def to_file(xml: str, filename: str) -> str:
    with open(filename, "w") as f:
        f.writelines(xml)


def urljoin(base: str, path: str) -> str:
    if not base.endswith("/"):
        base = base + "/"
    if path.startswith("/"):
        path = path[1:]
    return urllib.parse.urljoin(base, path)


def retry(ExceptionToCheck, tries=10, delay=10, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.
    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    timeunit = None
                    divisor = 1
                    if mdelay < 60:
                        timeunit = "seconds"
                        divisor = 1
                    elif timeunit < 3600:
                        timeunit = "minutes"
                        divisor = 60
                    elif timeunit < 3600 * 60:
                        timeunit = "hours"
                        divisor = 3600

                    msg = f"{str(e)}, Retrying in {int(mdelay/divisor)} {timeunit}..."

                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def load_xml(path: str) -> str:
    """load and return an xml file as a string

    Arguments:
        filename {str} -- filename of xml file. extension is optional.

    Returns:
        [type] -- [description]
    """

    xml = None
    ext = ".xml"
    if not path.endswith(ext):
        path = path + ext

    try:
        with open(path, "r") as f:
            xml = f.read()
    except Exception as fe:
        print(f"Invalid filename: {path}")

    return xml


if __name__ == "__main__":

    # @retry(Exception)
    # def testing():
    #     raise Exception("failed!")

    xml = load_xml("test/data", "well_header.xml")
