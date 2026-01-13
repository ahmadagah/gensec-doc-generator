"""
Entry point for the gensec-template CLI tool.

This module allows running the package directly with:
    python -m gensec_template
"""

from .cli import app


def main():
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
