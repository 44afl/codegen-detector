from functools import wraps

_loaded_models = set()

def mop_model_load(model_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            _loaded_models.add(model_name)
            print(f"[MOP] Model loaded: {model_name}")
            return result
        return wrapper
    return decorator


def mop_predict_only_if_loaded(model_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if model_name not in _loaded_models:
                raise RuntimeError(f"[MOP VIOLATION] {model_name} predict before load!")
            return func(*args, **kwargs)
        return wrapper
    return decorator
