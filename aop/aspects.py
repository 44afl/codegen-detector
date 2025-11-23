# aop/aspects.py
import time
from functools import wraps

def log_call(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

def timeit(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print(f"[TIME] {fn.__name__}: {end - start:.4f}s")
        return result
    return wrapper

def debug(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] {fn.__name__} args={args}, kwargs={kwargs}")
        res = fn(*args, **kwargs)
        print(f"[DEBUG] {fn.__name__} result={res}")
        return res
    return wrapper
