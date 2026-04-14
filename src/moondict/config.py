"""Configuration for MoonDict using Pydantic Settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ShortcutMode = Literal["push_to_talk", "toggle"]
TextInjectionBackend = Literal["xdotool", "clipboard"]


class MoonDictConfig(BaseSettings):
    """MoonDict application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="MOONDICT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Engine ──────────────────────────────────────────────
    engine: Literal["moonshine"] = "moonshine"
    model: Literal["base_es"] = "base_es"
    language: Literal["es", "en"] = "es"

    # ── Shortcuts ───────────────────────────────────────────
    shortcut_mode: ShortcutMode = "push_to_talk"
    shortcut_key: Literal["ctrl", "alt", "shift"] = "ctrl"

    # ── Audio ───────────────────────────────────────────────
    audio_device: int | None = None
    sample_rate: int = 16000
    audio_feedback: bool = True
    android_mic: bool = False

    # ── Text Injection ──────────────────────────────────────
    text_injection: TextInjectionBackend = "xdotool"
    copy_to_clipboard: bool = False

    # ── Paths ───────────────────────────────────────────────
    models_dir: Path = Field(
        default_factory=lambda: Path.home() / ".local" / "share" / "moondict" / "models"
    )
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".config" / "moondict"
    )

    # ── Logging ─────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
