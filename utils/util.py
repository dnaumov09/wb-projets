from ratelimit import limits, sleep_and_retry
from functools import wraps


def rate_limited(calls: int, period: int):
    def decorator(func):
        @sleep_and_retry
        @limits(calls=calls, period=period)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]