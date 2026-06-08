"""
This example demonstrates a simple text highlighter.
"""

from rich._console_entry import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme


class EmailHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an email."""

    base_style = "example."
    highlights = [r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)"]


theme = Theme({"example.email": "bold magenta"})
console = Console(highlighter=EmailHighlighter(), theme=theme)

if __name__ == "__main__":
    console.print("Send funds to money@example.org")
