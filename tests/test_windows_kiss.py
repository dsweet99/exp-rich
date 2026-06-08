"""Kiss static references for rich._windows."""

from rich._windows import WindowsConsoleFeatures, get_windows_console_features


def test_windows_features_only():
    features = get_windows_console_features()
    assert isinstance(features, WindowsConsoleFeatures)
    again = get_windows_console_features()
    assert again.vt == features.vt
    assert again.truecolor == features.truecolor

