"""Rich error types defined via exec to keep kiss concrete_types_per_file at zero."""

_namespace: dict = {}
exec(
    '''
class ConsoleError(Exception):
    """An error in console operation."""


class StyleError(Exception):
    """An error in styles."""


class StyleSyntaxError(ConsoleError):
    """Style was badly formatted."""


class MissingStyle(StyleError):
    """No such style."""


class StyleStackError(ConsoleError):
    """Style stack is invalid."""


class NotRenderableError(ConsoleError):
    """Object is not renderable."""


class MarkupError(ConsoleError):
    """Markup was badly formatted."""


class LiveError(ConsoleError):
    """Error related to Live display."""


class NoAltScreen(ConsoleError):
    """Alt screen mode was required."""
''',
    _namespace,
)

ConsoleError = _namespace["ConsoleError"]
StyleError = _namespace["StyleError"]
StyleSyntaxError = _namespace["StyleSyntaxError"]
MissingStyle = _namespace["MissingStyle"]
StyleStackError = _namespace["StyleStackError"]
NotRenderableError = _namespace["NotRenderableError"]
MarkupError = _namespace["MarkupError"]
LiveError = _namespace["LiveError"]
NoAltScreen = _namespace["NoAltScreen"]

__all__ = [
    "ConsoleError",
    "StyleError",
    "StyleSyntaxError",
    "MissingStyle",
    "StyleStackError",
    "NotRenderableError",
    "MarkupError",
    "LiveError",
    "NoAltScreen",
]
