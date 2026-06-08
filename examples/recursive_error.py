"""

Demonstrates Rich tracebacks for recursion errors.

Rich can exclude frames in the middle to avoid huge tracebacks.

"""

from rich.console import Console


def recursive_foo(n):
    return recursive_bar(n)


def recursive_bar(n):
    return recursive_foo(n)


console = Console()

if __name__ == "__main__":
    try:
        recursive_foo(1)
    except Exception:
        console.print_exception(max_frames=20)
