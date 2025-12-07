"""
smart_trace.py

Un mic utilitar pentru a vedea frumos:
- când intri / ieși dintr-o funcție
- cu ce argumente e apelată
- ce returnează
- cât durează

Folosește:
    @trace
sau:
    with Trace("nume"): ...
"""

import time
import inspect
import threading
from functools import wraps

# Lock pentru output thread-safe (utile dacă folosești multithreading)
_print_lock = threading.Lock()


def _short_repr(value, max_len=80):
    """
    Reprezentare scurtă și sigură pentru orice obiect.
    Taie string-ul dacă este prea lung.
    """
    try:
        text = repr(value)
    except Exception:
        text = f"<unrepr-able {type(value).__name__}>"

    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


class Trace:
    """
    Context manager care afișează intrarea și ieșirea dintr-un bloc,
    cu timp de execuție.

    Exemplu:
        with Trace("heavy stuff"):
            do_something()
    """

    _indent_level = 0
    _indent_step = 2

    def __init__(self, label: str):
        self.label = label
        self._start = None

    def __enter__(self):
        with _print_lock:
            indent = " " * (Trace._indent_level * Trace._indent_step)
            print(f"{indent}▶ {self.label}")
        Trace._indent_level += 1
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - self._start
        Trace._indent_level -= 1
        indent = " " * (Trace._indent_level * Trace._indent_step)

        with _print_lock:
            if exc is None:
                print(f"{indent}✔ {self.label} [{elapsed:.4f}s]")
            else:
                print(f"{indent}✖ {self.label} [{elapsed:.4f}s] -> {exc.__class__.__name__}: {exc}")
        # dacă returnăm False, excepția continuă să se propage (comportament normal)
        return False


def trace(func=None, *, name: str | None = None, show_args: bool = True, show_return: bool = True):
    """
    Decorator pentru trasarea unei funcții.

    Opțiuni:
        @trace
        @trace(name="custom")
        @trace(show_args=False, show_return=False)
    """

    def decorator(f):
        label = name or f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            # construim un string cu semnătura apelului
            if show_args:
                sig = inspect.signature(f)
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                call_repr = ", ".join(
                    f"{k}={_short_repr(v)}" for k, v in bound.arguments.items()
                )
                label_full = f"{label}({call_repr})"
            else:
                label_full = label

            with Trace(label_full):
                result = f(*args, **kwargs)

            if show_return:
                indent = " " * (Trace._indent_level * Trace._indent_step)
                with _print_lock:
                    print(f"{indent}↩ {label} -> {_short_repr(result)}")

            return result

        return wrapper

    # Permite atât @trace cât și @trace(...)
    if func is not None:
        return decorator(func)
    return decorator


# Exemplu de utilizare „de joacă”
if __name__ == "__main__":

    @trace
    def fib(n: int) -> int:
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    @trace(show_args=False, show_return=False)
    def slow_sum(n: int) -> int:
        total = 0
        with Trace("looping"):
            for i in range(n):
                total += i
        return total

    with Trace("demo"):
        x = fib(5)
        y = slow_sum(10000)
        print("Rezultate finale:", x, y)
