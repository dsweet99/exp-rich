# coding=utf-8

MARKDOWN = """Heading
=======

Sub-heading
-----------

### Heading

#### H4 Heading

##### H5 Heading

###### H6 Heading


Paragraphs are separated
by a blank line.

Two spaces at the end of a line
produces a line break.

Text attributes _italic_,
**bold**, `monospace`.

Horizontal rule:

---

Bullet list:

  * apples
  * oranges
  * pears

Numbered list:

  1. lather
  2. rinse
  3. repeat

An [example](http://example.com).

> Markdown uses email-style > characters for blockquoting.
>
> Lorem ipsum

![progress](https://github.com/textualize/rich/raw/master/imgs/progress.gif)


```
a=1
```

```python
import this
```

```somelang
foobar
```

"""

from .render import render


def _Markdown(*args, **kwargs):
    from rich.markdown import Markdown

    return Markdown(*args, **kwargs)


def test_markdown_render():
    markdown = _Markdown(MARKDOWN, hyperlinks=False)
    rendered_markdown = render(markdown)
    print(repr(rendered_markdown))
    expected = "                                              \x1b[1;4mHeading\x1b[0m                                               \n\n\x1b[4;35mSub-heading\x1b[0m                                                                                         \n\n\x1b[1;35mHeading\x1b[0m                                                                                             \n\n\x1b[3;35mH4 Heading\x1b[0m                                                                                          \n\n\x1b[3mH5 Heading\x1b[0m                                                                                          \n\n\x1b[2mH6 Heading\x1b[0m                                                                                          \n\nParagraphs are separated by a blank line.                                                           \n\nTwo spaces at the end of a line produces a line break.                                              \n\nText attributes \x1b[3mitalic\x1b[0m, \x1b[1mbold\x1b[0m, \x1b[1;36;40mmonospace\x1b[0m.                                                            \n\nHorizontal rule:                                                                                    \n\n\x1b[2m----------------------------------------------------------------------------------------------------\x1b[0m\n\nBullet list:                                                                                        \n\n\x1b[1m • \x1b[0mapples                                                                                           \n\x1b[1m • \x1b[0moranges                                                                                          \n\x1b[1m • \x1b[0mpears                                                                                            \n\nNumbered list:                                                                                      \n\n\x1b[36m 1 \x1b[0mlather                                                                                           \n\x1b[36m 2 \x1b[0mrinse                                                                                            \n\x1b[36m 3 \x1b[0mrepeat                                                                                           \n\nAn \x1b[94mexample\x1b[0m (\x1b[4;34mhttp://example.com\x1b[0m).                                                                    \n\n\x1b[35m▌ \x1b[0m\x1b[35mMarkdown uses email-style > characters for blockquoting.\x1b[0m\x1b[35m                                        \x1b[0m\n\x1b[35m▌ \x1b[0m\x1b[35mLorem ipsum\x1b[0m\x1b[35m                                                                                     \x1b[0m\n\n🌆 progress                                                                                         \n\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n\x1b[48;2;39;40;34m \x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34ma=1\x1b[0m\x1b[48;2;39;40;34m                                                                                               \x1b[0m\x1b[48;2;39;40;34m \x1b[0m\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n\x1b[48;2;39;40;34m \x1b[0m\x1b[38;2;255;70;137;48;2;39;40;34mimport\x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34m \x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34mthis\x1b[0m\x1b[48;2;39;40;34m                                                                                       \x1b[0m\x1b[48;2;39;40;34m \x1b[0m\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n\x1b[48;2;39;40;34m \x1b[0m\x1b[38;2;248;248;242;48;2;39;40;34mfoobar\x1b[0m\x1b[48;2;39;40;34m                                                                                            \x1b[0m\x1b[48;2;39;40;34m \x1b[0m\n\x1b[48;2;39;40;34m                                                                                                    \x1b[0m\n"
    assert rendered_markdown == expected


if __name__ == "__main__":
    markdown = _Markdown(MARKDOWN, hyperlinks=False)
    rendered = render(markdown)
    print(rendered)
    print(repr(rendered))
