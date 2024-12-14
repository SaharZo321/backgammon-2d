import functools
from threading import Timer, Thread
from time import sleep
import time
from typing import Any, Callable

from game_manager import GameManager


def debounce(timeout: float):
    """
    Decorator that will debounce a function. The function will be executed after timeout seconds
    if there will be no additional calls during the timeout period.
    """

    def decorator(func):
        timer = Timer(timeout, lambda: None)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            timer.cancel()
            timer = Timer(timeout, func, args, kwargs)
            timer.start()

        return wrapper

    return decorator

def throttle(timeout: float):
    """
    Decorator that will throttle a function. The function will not be executed until timeout is finished.
    """

    def decorator(func):
        timer = 0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            if time.time() - timer < timeout:
                return
            timer = time.time()
            func(*args, **kwargs)

        return wrapper

    return decorator

def repeat(num: int):
    """
    Decorator that will repeat a function num times.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num):
                func(*args, **kwargs)

        return wrapper

    return decorator


def run_threaded(daemon=False):
    """
    Decorator that will run the function on another thread. The function will return the working thread.
    """

    def decorator(func: Callable[..., None]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Thread:
            thread = Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            thread.start()
            print(f"Ran {wrapper.__name__} on {thread}")
            return thread

        return wrapper

    return decorator

        
# @debounce(2)
# def idk(h: str):
#     print(f"idk: {h}")


# idk("hello")
# idk("hello")
# print("dfljd")
# idk("hello")
# idk("hello")
# sleep(1)
# idk("hello")