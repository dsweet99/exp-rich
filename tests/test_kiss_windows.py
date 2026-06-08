from rich._windows import WindowsConsoleFeatures, get_windows_console_features


def test_windows_console_features_call():
    features = get_windows_console_features()
    assert isinstance(features, WindowsConsoleFeatures)
    assert get_windows_console_features is not None
