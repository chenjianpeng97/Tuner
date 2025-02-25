import time
from functools import wraps


def retry(max_tries=3, delay_seconds=1):
    """
    Usage:
    @retry(max_tries=5, delay_seconds=2)
    def call_dummy_api():
        response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
        return response
    """
    def decorator_retry(func):
        @wraps(func)
        def wrapper_retry(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tries += 1
                    if tries == max_tries:
                        raise e
                    time.sleep(delay_seconds)

        return wrapper_retry

    return decorator_retry


