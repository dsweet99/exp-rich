"""Markdown rendering smoke test without static rich imports."""

from __future__ import annotations

import subprocess
import sys
import textwrap


def test_markdown_render_common_elements():
    script = textwrap.dedent(
        """
        import io
        from rich._console_entry import Console
        from rich.markdown import Markdown

        md = Markdown("# Title\\n\\n**bold** and `code`\\n\\n- item\\n\\n> quote")
        console = Console(file=io.StringIO(), width=100)
        console.print(md)
        print(console.file.getvalue())
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    output = result.stdout
    assert "Title" in output
    assert "bold" in output
    assert "item" in output
