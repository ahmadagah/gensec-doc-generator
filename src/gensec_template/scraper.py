"""
Web scraper for the lab template CLI tool.

This module provides functionality to scrape lab data from a course
website, including the lab index and individual lab sections.
"""

import asyncio
import time
from typing import Optional

import httpx

from .models import Lab, LabIndex, Section
from .parser import (
    parse_lab_index_html,
    parse_lab_page_html,
    parse_lab_section_html,
    get_section_count,
)


# Default configuration
DEFAULT_BASE_URL = "https://codelabs.cs.pdx.edu/cs475/"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

# User agent for requests
USER_AGENT = "gensec-template/0.1.0 (Lab Template Generator)"


class ScraperError(Exception):
    """Exception raised for scraper errors."""

    pass


class Scraper:
    """
    Web scraper for lab content.

    Provides methods to fetch and parse lab data from the course website
    with retry logic and error handling.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the scraper.

        Args:
            base_url: Base URL for the course website.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            retry_delay: Initial delay between retries in seconds.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def fetch_page(self, url: str) -> str:
        """
        Fetch a page with retry logic.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content of the page.

        Raises:
            ScraperError: If the page cannot be fetched after retries.
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    headers=self.headers,
                    follow_redirects=True,
                ) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text

            except httpx.TimeoutException as e:
                last_error = e
                delay = self.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    last_error = e
                    delay = self.retry_delay * (2**attempt)
                    await asyncio.sleep(delay)
                else:
                    raise ScraperError(f"HTTP error {e.response.status_code}: {url}") from e

            except httpx.RequestError as e:
                last_error = e
                delay = self.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

        raise ScraperError(
            f"Failed to fetch {url} after {self.max_retries} attempts: {last_error}"
        )

    def fetch_page_sync(self, url: str) -> str:
        """
        Synchronous wrapper for fetch_page.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content of the page.
        """
        return asyncio.run(self.fetch_page(url))

    async def scrape_lab_index(self) -> LabIndex:
        """
        Scrape the main course page to get all available labs.

        Returns:
            A LabIndex containing all discovered labs (without sections).
        """
        html = await self.fetch_page(self.base_url)
        labs = parse_lab_index_html(html, self.base_url)

        return LabIndex(labs=labs)

    def scrape_lab_index_sync(self) -> LabIndex:
        """
        Synchronous wrapper for scrape_lab_index.

        Returns:
            A LabIndex containing all discovered labs.
        """
        return asyncio.run(self.scrape_lab_index())

    async def scrape_lab_sections(self, lab: Lab) -> Lab:
        """
        Scrape all sections for a specific lab.

        Args:
            lab: The Lab object to populate with sections.

        Returns:
            The Lab with populated sections.
        """
        # Fetch the main lab page (all sections are in one HTML file)
        html = await self.fetch_page(lab.url)
        lab_title, section_titles = parse_lab_page_html(html)

        # Update lab title if we got a better one
        if lab_title and not lab.title:
            lab.title = lab_title

        # Determine number of sections
        num_sections = get_section_count(html)
        if not num_sections and section_titles:
            num_sections = len(section_titles)
        if not num_sections:
            num_sections = 10  # Default to trying 10 sections

        # Parse each section from the same HTML (no need to refetch)
        sections = []
        for i in range(num_sections):
            # Parse section from the single HTML page
            section = parse_lab_section_html(html, i + 1)

            # Use section title from navigation if available and section has no title
            if i < len(section_titles) and section_titles[i]:
                if not section.title:
                    section.title = section_titles[i]

            # Only add sections that have a title or questions
            if section.title or section.questions:
                sections.append(section)

        lab.sections = sections
        return lab

    def scrape_lab_sections_sync(self, lab: Lab) -> Lab:
        """
        Synchronous wrapper for scrape_lab_sections.

        Args:
            lab: The Lab object to populate with sections.

        Returns:
            The Lab with populated sections.
        """
        return asyncio.run(self.scrape_lab_sections(lab))

    async def scrape_full_lab(self, lab_id_or_number: str) -> Optional[Lab]:
        """
        Scrape a complete lab by its ID or number.

        Args:
            lab_id_or_number: The lab ID (e.g., "G01.3_ProgramModel") or
                              number (e.g., "01.3").

        Returns:
            The fully populated Lab, or None if not found.
        """
        # First get the lab index
        index = await self.scrape_lab_index()

        # Find the lab
        lab = index.get_lab_by_id(lab_id_or_number)
        if not lab:
            lab = index.get_lab_by_number(lab_id_or_number)

        if not lab:
            return None

        # Scrape the sections
        return await self.scrape_lab_sections(lab)

    def scrape_full_lab_sync(self, lab_id_or_number: str) -> Optional[Lab]:
        """
        Synchronous wrapper for scrape_full_lab.

        Args:
            lab_id_or_number: The lab ID or number.

        Returns:
            The fully populated Lab, or None if not found.
        """
        return asyncio.run(self.scrape_full_lab(lab_id_or_number))


# Global scraper instance
_scraper: Optional[Scraper] = None


def get_scraper() -> Scraper:
    """
    Get the global scraper instance.

    Returns:
        The global Scraper instance.
    """
    global _scraper
    if _scraper is None:
        _scraper = Scraper()
    return _scraper


# Convenience functions for sync usage
def scrape_lab_index() -> LabIndex:
    """Scrape the lab index (synchronous)."""
    return get_scraper().scrape_lab_index_sync()


def scrape_lab(lab_id_or_number: str) -> Optional[Lab]:
    """Scrape a full lab (synchronous)."""
    return get_scraper().scrape_full_lab_sync(lab_id_or_number)


def fetch_page(url: str) -> str:
    """Fetch a page (synchronous)."""
    return get_scraper().fetch_page_sync(url)
