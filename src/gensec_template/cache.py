"""
Caching utilities for the gensec-template CLI tool.

This module provides persistent caching functionality for scraped lab data
using diskcache. Cache entries support time-to-live (TTL) settings.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import diskcache

from .models import Lab, LabIndex


# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "gensec-template"

# Default TTL: 24 hours in seconds
DEFAULT_TTL = 24 * 60 * 60

# Cache keys
LAB_INDEX_KEY = "lab_index"
LAB_PREFIX = "lab:"


@dataclass
class CacheInfo:
    """Information about the cache state."""

    directory: str
    size_bytes: int
    entry_count: int
    lab_index_cached: bool
    lab_index_age: Optional[str]
    cached_labs: list[str]


class LabCache:
    """
    Persistent cache for lab data.

    Uses diskcache for storing scraped lab index and individual lab data
    with configurable time-to-live.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl: int = DEFAULT_TTL,
    ):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.cache/gensec-template/
            ttl: Time-to-live for cache entries in seconds. Defaults to 24 hours.
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self._cache = diskcache.Cache(str(self.cache_dir))

    def get_lab_index(self) -> Optional[LabIndex]:
        """
        Get the cached lab index.

        Returns:
            The cached LabIndex if present and not expired, None otherwise.
        """
        try:
            data = self._cache.get(LAB_INDEX_KEY)
            if data is not None:
                return LabIndex.from_dict(data)
        except Exception:
            pass
        return None

    def set_lab_index(self, index: LabIndex) -> None:
        """
        Cache the lab index.

        Args:
            index: The LabIndex to cache.
        """
        try:
            self._cache.set(LAB_INDEX_KEY, index.to_dict(), expire=self.ttl)
        except Exception:
            pass

    def get_lab(self, lab_id: str) -> Optional[Lab]:
        """
        Get a cached lab by its ID.

        Args:
            lab_id: The lab ID to look up.

        Returns:
            The cached Lab if present and not expired, None otherwise.
        """
        try:
            key = f"{LAB_PREFIX}{lab_id}"
            data = self._cache.get(key)
            if data is not None:
                return Lab.from_dict(data)
        except Exception:
            pass
        return None

    def set_lab(self, lab: Lab) -> None:
        """
        Cache a lab.

        Args:
            lab: The Lab to cache.
        """
        try:
            key = f"{LAB_PREFIX}{lab.lab_id}"
            self._cache.set(key, lab.to_dict(), expire=self.ttl)
        except Exception:
            pass

    def clear_cache(self) -> None:
        """Clear all cached data."""
        try:
            self._cache.clear()
        except Exception:
            pass

    def get_cache_info(self) -> CacheInfo:
        """
        Get information about the cache state.

        Returns:
            A CacheInfo object with cache statistics.
        """
        # Calculate cache size
        size_bytes = 0
        try:
            for entry in os.scandir(self.cache_dir):
                if entry.is_file():
                    size_bytes += entry.stat().st_size
        except Exception:
            pass

        # Count entries
        entry_count = len(self._cache)

        # Check lab index
        lab_index_cached = LAB_INDEX_KEY in self._cache
        lab_index_age = None

        if lab_index_cached:
            try:
                index = self.get_lab_index()
                if index and index.last_updated:
                    updated = datetime.fromisoformat(index.last_updated)
                    delta = datetime.now() - updated
                    hours = delta.total_seconds() / 3600
                    if hours < 1:
                        lab_index_age = f"{int(delta.total_seconds() / 60)} minutes ago"
                    elif hours < 24:
                        lab_index_age = f"{int(hours)} hours ago"
                    else:
                        lab_index_age = f"{int(hours / 24)} days ago"
            except Exception:
                pass

        # Get list of cached labs
        cached_labs = []
        for key in self._cache:
            if key.startswith(LAB_PREFIX):
                cached_labs.append(key[len(LAB_PREFIX) :])

        return CacheInfo(
            directory=str(self.cache_dir),
            size_bytes=size_bytes,
            entry_count=entry_count,
            lab_index_cached=lab_index_cached,
            lab_index_age=lab_index_age,
            cached_labs=cached_labs,
        )

    def close(self) -> None:
        """Close the cache."""
        try:
            self._cache.close()
        except Exception:
            pass

    def __enter__(self) -> "LabCache":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# Global cache instance
_cache: Optional[LabCache] = None


def get_cache() -> LabCache:
    """
    Get the global cache instance.

    Returns:
        The global LabCache instance.
    """
    global _cache
    if _cache is None:
        _cache = LabCache()
    return _cache


def clear_global_cache() -> None:
    """Clear the global cache and reset the instance."""
    global _cache
    if _cache is not None:
        _cache.clear_cache()
        _cache.close()
        _cache = None
