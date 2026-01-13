"""
Configuration management for the lab template CLI tool.

Supports multiple configuration sources with the following priority:
1. CLI arguments (highest priority)
2. Environment variables
3. Config file (~/.config/gensec-template/config.json)
4. Default values (lowest priority)
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_BASE_URL = "https://codelabs.cs.pdx.edu/cs475/"
CONFIG_DIR = Path.home() / ".config" / "gensec-template"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Environment variable names
ENV_BASE_URL = "LAB_TEMPLATE_URL"


@dataclass
class Config:
    """Application configuration."""

    base_url: str = DEFAULT_BASE_URL
    cache_ttl_hours: int = 24

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "base_url": self.base_url,
            "cache_ttl_hours": self.cache_ttl_hours,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        return cls(
            base_url=data.get("base_url", DEFAULT_BASE_URL),
            cache_ttl_hours=data.get("cache_ttl_hours", 24),
        )


def load_config_file() -> Optional[Config]:
    """
    Load configuration from the config file.

    Returns:
        Config object if file exists and is valid, None otherwise.
    """
    if not CONFIG_FILE.exists():
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Config.from_dict(data)
    except (json.JSONDecodeError, IOError):
        return None


def save_config_file(config: Config) -> bool:
    """
    Save configuration to the config file.

    Args:
        config: The Config object to save.

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)
        return True
    except IOError:
        return False


def get_config(cli_url: Optional[str] = None) -> Config:
    """
    Get the effective configuration from all sources.

    Priority (highest to lowest):
    1. CLI argument (cli_url parameter)
    2. Environment variable (LAB_TEMPLATE_URL)
    3. Config file (~/.config/gensec-template/config.json)
    4. Default values

    Args:
        cli_url: Optional URL passed via CLI flag.

    Returns:
        The effective Config object.
    """
    # Start with defaults
    config = Config()

    # Load from config file (lowest priority after defaults)
    file_config = load_config_file()
    if file_config:
        config = file_config

    # Override with environment variable
    env_url = os.environ.get(ENV_BASE_URL)
    if env_url:
        config.base_url = env_url

    # Override with CLI argument (highest priority)
    if cli_url:
        config.base_url = cli_url

    return config


def get_config_info() -> dict:
    """
    Get information about current configuration sources.

    Returns:
        Dictionary with configuration source information.
    """
    info = {
        "config_file": str(CONFIG_FILE),
        "config_file_exists": CONFIG_FILE.exists(),
        "env_var": ENV_BASE_URL,
        "env_var_set": ENV_BASE_URL in os.environ,
        "default_url": DEFAULT_BASE_URL,
    }

    # Determine effective source
    if ENV_BASE_URL in os.environ:
        info["effective_source"] = "environment"
        info["effective_url"] = os.environ[ENV_BASE_URL]
    elif CONFIG_FILE.exists():
        file_config = load_config_file()
        if file_config:
            info["effective_source"] = "config_file"
            info["effective_url"] = file_config.base_url
        else:
            info["effective_source"] = "default"
            info["effective_url"] = DEFAULT_BASE_URL
    else:
        info["effective_source"] = "default"
        info["effective_url"] = DEFAULT_BASE_URL

    return info
