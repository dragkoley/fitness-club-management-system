from functools import wraps
import time
from typing import Any, Callable

from src.utils.logger import AppLogger


def monitor_action(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = AppLogger.get_instance()
        method_name = f"{args[0].__class__.__name__}.{func.__name__}" if args else func.__name__

        logger.log_info("[Decorator] Starting execution of %s", method_name)
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000

            logger.log_info("[Decorator] %s finished successfully in %s ms", method_name, f"{execution_time:.2f}")
            return result

        except Exception as e:
            logger.log_error("[Decorator] Exception caught in %s. Details: %s", method_name, e)

    return wrapper
