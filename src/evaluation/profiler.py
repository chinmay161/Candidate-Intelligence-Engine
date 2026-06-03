from functools import wraps
from typing import Callable, Any
from .runtime_profiler import RuntimeProfiler
from .memory_profiler import MemoryProfiler

# Global instances for decorators (optional, but convenient for some setups)
_global_runtime_profiler = RuntimeProfiler()
_global_memory_profiler = MemoryProfiler()

def profile_runtime(phase_name: str, profiler: RuntimeProfiler = None):
    """
    Decorator to profile the runtime of a function and record it in the given profiler.
    If no profiler is provided, uses a global instance.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            p = profiler or _global_runtime_profiler
            p.start(phase_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                p.stop(phase_name)
        return wrapper
    return decorator

def get_global_runtime_profiler() -> RuntimeProfiler:
    return _global_runtime_profiler

def get_global_memory_profiler() -> MemoryProfiler:
    return _global_memory_profiler
