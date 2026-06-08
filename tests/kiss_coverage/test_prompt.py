"""Kiss static coverage for rich.prompt."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.prompt

def test_kiss_prompt_symbols_0():
    _mod = _import_rich('prompt')
    Confirm = getattr(_mod, 'Confirm')
    FloatPrompt = getattr(_mod, 'FloatPrompt')
    IntPrompt = getattr(_mod, 'IntPrompt')
    InvalidResponse = getattr(_mod, 'InvalidResponse')
    Prompt = getattr(_mod, 'Prompt')
    PromptBase = getattr(_mod, 'PromptBase')
    PromptError = getattr(_mod, 'PromptError')
    assert Confirm is not None
    assert FloatPrompt is not None
    assert IntPrompt is not None
    assert InvalidResponse is not None
    assert Prompt is not None
    assert PromptBase is not None
    assert PromptError is not None
