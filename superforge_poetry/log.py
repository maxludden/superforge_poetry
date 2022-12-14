# superforge_poetry/log.py

from platform import platform
from os import environ
from time import perf_counter

from loguru import logger as log
from rich.console import Console, ConsoleOptions
from rich.traceback import install
from rich.logging import RichHandler
from functools import wraps


# .┌─────────────────────────────────────────────────────────────────┐<#
# .│                           Console                               │<#
# .└─────────────────────────────────────────────────────────────────┘<#
max_console = Console()
max_console.clear()
install(console=max_console, theme="monokai", show_locals=True, word_wrap=True)


# >┌─────────────────────────────────────────────────────────────────┐<#
# >│                              BASE                               │<#
# >└─────────────────────────────────────────────────────────────────┘<#
def generate_base():
    """
    Generate the root fo the project.
    """
    if platform() == "Linux":
        ROOT = "home"
    else:
        ROOT = "Users"  # > Mac
    BASE = f"/{ROOT}/maxludden/dev/py/superforge_poetry"
    return BASE


BASE = generate_base()
environ["BASE"] = BASE


# .┌─────────────────────────────────────────────────────────────────┐#
# .│                          Current Run                            │#
# .└─────────────────────────────────────────────────────────────────┘#
def get_last_run() -> int:
    """
    Get the last run of the script.
    """
    with open(f"{BASE}/run.txt", "r") as infile:
        last_run = int(infile.read())
    return last_run


def increment_run(last_run: int) -> int:
    """
    Increment the last run of the script.
    """
    run = last_run + 1
    return run


def record_run(run: int) -> None:
    """
    Record the last run of the script.
    """
    with open(f"{BASE}/run.txt", "w") as outfile:
        outfile.write(str(run))


def new_run() -> int:
    """
    Create a new run of the script.
    """
    last_run = get_last_run()
    run = increment_run(last_run)
    record_run(run)
    max_console.rule(title=f"\n\n\nRun {run}\n\n\n")
    return run


current_run = new_run()
# End of run


# >┌─────────────────────────────────────────────────────────────────┐<#
# >│                               Log                               │<#
# >└─────────────────────────────────────────────────────────────────┘<#
log.configure(
    handlers=[
        dict(
            sink=f"{BASE}/logs/debug.log",
            level="DEBUG",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8}ﰲ  {message}",
            rotation="10 MB",
        ),
        dict(
            sink=(
                lambda msg: max_console.log(
                    msg, markup=True, highlight=True, log_locals=True
                )
            ),
            level="INFO",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: ^8} ﰲ  {message}",
        ),
        # RichHandler(
        #     level="ERROR",
        #     format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8}ﰲ  {message}",
        #     rich_traceback=True,
        #     log_locals=True,
        #     highlight=True,
        # ),
    ],
    extra={"run": current_run},
)

log.debug("Initialized Logger")


# .┌─────────────────────────────────────────────────────────────────┐#
# .│                           Decorators                            │#
# .└─────────────────────────────────────────────────────────────────┘#
def check(
    *,
    entry=True,
    exit=True,
    level="DEBUG",
):
    """Create a decorator that can be used to record the entry, *args, **kwargs,as well ass the exit and results of a decorated function.

    Args:
        entry (bool, optional):
            Should the entry , *args, and **kwargs of given decorated function be logged? Defaults to True.

        exit (bool, optional):
            Should the exit and the result of given decorated function be logged? Defaults to True.

        level (str, optional):
            The level at which to log to be recorded.. Defaults to "DEBUG".
    """

    def wrapper(func):
        name = func.__name__
        log.debug(f"Checking function {name}.")

        @wraps(func)
        def wrapped(*args, **kwargs):
            time_log = log.opt(depth=1)
            if entry:
                time_log.log(
                    level,
                    f"Entering '{name}'\n<code>\nargs:\n{args}'\nkwargs={kwargs}</code>",
                )
            result = func(*args, **kwargs)
            if exit:
                time_log.log(
                    level, f"Exiting '{name}'<code>\nresult:\n<{result}</code>"
                )
            return result

        return wrapped

    return wrapper


def time(*, level="DEBUG"):
    """Create a decorator that can be used to record the entry and exit of a decorated function.
    Args:
        level (str, optional):
            The level at which to log to be recorded.. Defaults to "DEBUG".
    """

    def wrapper(func):
        name = func.__name__
        log.debug(f"Timing function {name}.")

        @wraps(func)
        def wrapped(*args, **kwargs):
            time_log = log.opt(depth=1)
            start = perf_counter()
            result = func(*args, **kwargs)
            end = perf_counter()
            time_log.log(f"{name} took {end - start} seconds.")
            return result

        return wrapped

    return wrapper
