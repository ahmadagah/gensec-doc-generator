"""
gensec-template: CLI tool for generating lab documentation templates.

This package provides data models and utilities for scraping, parsing,
and generating documentation templates from course lab materials.
"""

from .models import (
    Question,
    Section,
    Lab,
    LabIndex,
)

__all__ = [
    "Question",
    "Section",
    "Lab",
    "LabIndex",
]

__version__ = "0.1.0"
