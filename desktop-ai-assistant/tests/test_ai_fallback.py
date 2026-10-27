
"""Tests for Gemini-to-Ollama fallback behavior."""

import pytest

from assistant.ai import client
from assistant.ai.errors import NoApiKeyError


def test_gemini_success_does_not_call_ollama(monkeypatch):
    def fake_gemini(prompt, image=None, mode="general"):
        yield "Hello "
        yield "world"

    def unexpected_ollama(*args, **kwargs):
        pytest.fail("Ollama should not be called when Gemini succeeds")

    monkeypatch.setattr(client, "ask_gemini", fake_gemini)
    monkeypatch.setattr(client, "ask_ollama", unexpected_ollama)

    assert list(client.ask("Hi")) == ["Hello ", "world"]


def test_missing_gemini_key_falls_back_to_ollama(monkeypatch):
    def fake_gemini(prompt, image=None, mode="general"):
        raise NoApiKeyError("No API key configured")
        yield  # Makes this function a generator.

    def fake_ollama(prompt, image=None, mode="general"):
        yield "Local "
        yield "response"

    monkeypatch.setattr(client, "ask_gemini", fake_gemini)
    monkeypatch.setattr(client, "ask_ollama", fake_ollama)

    assert list(client.ask("Hi")) == ["Local ", "response"]


def test_no_fallback_after_gemini_has_started_streaming(monkeypatch):
    def fake_gemini(prompt, image=None, mode="general"):
        yield "Partial "
        raise NoApiKeyError("Unexpected provider error")

    def unexpected_ollama(*args, **kwargs):
        pytest.fail("Ollama should not start after Gemini yielded text")

    monkeypatch.setattr(client, "ask_gemini", fake_gemini)
    monkeypatch.setattr(client, "ask_ollama", unexpected_ollama)

    with pytest.raises(NoApiKeyError):
        list(client.ask("Hi"))
