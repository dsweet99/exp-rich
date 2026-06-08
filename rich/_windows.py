import sys

from ._windows_console_features import WindowsConsoleFeatures


def _get_windows_console_features() -> WindowsConsoleFeatures:
    """Get windows console features."""
    try:
        import ctypes
        from ctypes import LibraryLoader

        if sys.platform != "win32":
            raise ImportError("Not windows")

        LibraryLoader(ctypes.WinDLL)
        from ._win32_console import (
            ENABLE_VIRTUAL_TERMINAL_PROCESSING,
            GetConsoleMode,
            GetStdHandle,
            LegacyWindowsError,
        )
    except (AttributeError, ImportError, ValueError):
        return WindowsConsoleFeatures()

    handle = GetStdHandle()
    try:
        console_mode = GetConsoleMode(handle)
        success = True
    except LegacyWindowsError:
        console_mode = 0
        success = False
    vt = bool(success and console_mode & ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    truecolor = False
    if vt:
        win_version = sys.getwindowsversion()
        truecolor = win_version.major > 10 or (
            win_version.major == 10 and win_version.build >= 15063
        )
    return WindowsConsoleFeatures(vt=vt, truecolor=truecolor)


get_windows_console_features = _get_windows_console_features

