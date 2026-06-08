ConsoleError = type("ConsoleError", (Exception,), {"__doc__": "An error in console operation."})

StyleError = type("StyleError", (Exception,), {"__doc__": "An error in styles."})

StyleSyntaxError = type(
    "StyleSyntaxError", (ConsoleError,), {"__doc__": "Style was badly formatted."}
)

MissingStyle = type("MissingStyle", (StyleError,), {"__doc__": "No such style."})

StyleStackError = type(
    "StyleStackError", (ConsoleError,), {"__doc__": "Style stack is invalid."}
)

NotRenderableError = type(
    "NotRenderableError", (ConsoleError,), {"__doc__": "Object is not renderable."}
)

MarkupError = type(
    "MarkupError", (ConsoleError,), {"__doc__": "Markup was badly formatted."}
)

LiveError = type("LiveError", (ConsoleError,), {"__doc__": "Error related to Live display."})

NoAltScreen = type(
    "NoAltScreen", (ConsoleError,), {"__doc__": "Alt screen mode was required."}
)
