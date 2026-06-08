"""

Demonstrates Rich tracebacks for recursion errors.

Rich can exclude frames in the middle to avoid huge tracebacks.

"""

from rich._console_entry import Console


def recursive_demo_foo(n):
    return recursive_demo_bar(n)


def recursive_demo_bar(n):
    return recursive_demo_foo(n)


console = Console()

if __name__ == "__main__":
    try:
        recursive_demo_foo(1)
    except Exception:
        console.print_exception(max_frames=20)
