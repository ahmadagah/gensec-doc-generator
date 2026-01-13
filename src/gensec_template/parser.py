"""
HTML parser for the gensec-template CLI tool.

This module provides functionality to parse HTML content from the GenSec
lab website and extract structured data about labs, sections, and questions.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import Lab, Section, Question


# Action verbs that indicate a deliverable (at start of bullet)
DELIVERABLE_STARTERS = [
    "take a screenshot",
    "submit",
    "demonstrate",
    "explain",
    "show",
    "include",
    "provide",
    "document",
    "answer",
    "describe",
    "compare",
    "analyze",
    "list",
    "identify",
    "discuss",
    "report",
    "capture",
]

# Words that indicate NOT a deliverable (instructional)
EXCLUSION_INDICATORS = [
    "edit the file",
    "run the command",
    "install",
    "navigate to",
    "click on",
    "open the",
    "create a",
    "copy the",
    "paste the",
    "download",
    "execute the",
    "type the",
    "enter the",
    "set the",
    "configure",
]


def parse_lab_index_html(html: str, base_url: str) -> list[Lab]:
    """
    Parse the main course page HTML to extract all available labs.

    Args:
        html: The HTML content of the main course page.
        base_url: The base URL for constructing absolute lab URLs.

    Returns:
        A list of Lab objects with basic information (no sections populated).
    """
    soup = BeautifulSoup(html, "lxml")
    labs = []

    # Find all lab cards - they are <a> tags with href containing "/labs/"
    # Try multiple selectors for different site structures
    cards = soup.find_all("a", class_="codelab-card")

    # If no codelab-card class found, look for links to labs
    if not cards:
        cards = soup.find_all("a", href=re.compile(r"/labs/G\d+"))

    for card in cards:
        try:
            # Extract href for URL
            href = card.get("href", "")
            if not href or "/labs/" not in href:
                continue

            # Build full URL
            lab_url = urljoin(base_url, href)

            # Extract lab ID from href (e.g., "/labs/G01.3_ProgramModel/...")
            lab_id_match = re.search(r"/labs/([^/]+)/", href)
            lab_id = lab_id_match.group(1) if lab_id_match else ""

            # Extract lab number from the card
            # Look for h4, h3, h2, or any heading with title pattern
            title_elem = (
                card.find("h4") or
                card.find("h3") or
                card.find("h2", class_="title") or
                card.find("div", class_="title") or
                card.find("h2")
            )
            title_text = title_elem.get_text(strip=True) if title_elem else ""

            # Parse lab number and title
            # Format is usually "01.3: Programmatic Model Access"
            number_match = re.match(r"^(\d+\.\d+)[:\s-]*(.+)$", title_text)
            if number_match:
                lab_number = number_match.group(1)
                lab_title = number_match.group(2).strip()
            else:
                # Try to extract from lab_id
                id_match = re.match(r"G(\d+\.\d+)_", lab_id)
                lab_number = id_match.group(1) if id_match else ""
                lab_title = title_text

            # Extract duration - look for span with duration or text containing "min"
            duration_elem = card.find("span", class_="duration")
            if not duration_elem:
                # Look for any span containing duration info
                for span in card.find_all("span"):
                    span_text = span.get_text(strip=True)
                    if "min" in span_text.lower():
                        duration_elem = span
                        break

            duration_text = duration_elem.get_text(strip=True) if duration_elem else ""
            duration_match = re.search(r"(\d+)\s*min", duration_text, re.IGNORECASE)
            duration = int(duration_match.group(1)) if duration_match else None

            # Extract description from <p> tag
            desc_elem = card.find("p") or card.find("div", class_="description")
            description = desc_elem.get_text(strip=True) if desc_elem else None

            lab = Lab(
                number=lab_number,
                lab_id=lab_id,
                title=lab_title,
                url=lab_url,
                sections=[],
                duration_minutes=duration,
                description=description,
            )
            labs.append(lab)

        except Exception:
            # Skip malformed cards
            continue

    return labs


def parse_lab_page_html(html: str) -> tuple[str, list[str]]:
    """
    Parse a lab page HTML to extract the title and section titles.

    Args:
        html: The HTML content of a lab page.

    Returns:
        A tuple of (lab_title, list_of_section_titles).
    """
    soup = BeautifulSoup(html, "lxml")

    # Extract main lab title from google-codelab element or title tag
    codelab = soup.find("google-codelab")
    if codelab and codelab.get("title"):
        lab_title = codelab.get("title", "")
    else:
        title_elem = soup.find("title") or soup.find("h1")
        lab_title = title_elem.get_text(strip=True) if title_elem else ""

    # Extract section titles from google-codelab-step elements
    section_titles = []

    # Look for google-codelab-step elements (the actual content structure)
    steps = soup.find_all("google-codelab-step")
    for step in steps:
        label = step.get("label", "")
        if label:
            section_titles.append(label)

    # If no steps found, try sidebar navigation
    if not section_titles:
        nav_steps = soup.find_all("li", class_="step") or soup.find_all("a", class_="step")
        for step in nav_steps:
            label = step.find("span", class_="label")
            if label:
                section_titles.append(label.get_text(strip=True))
            else:
                step_text = step.get_text(strip=True)
                if step_text:
                    section_titles.append(step_text)

    return lab_title, section_titles


def parse_lab_section_html(html: str, section_number: int) -> Section:
    """
    Parse a lab section HTML to extract the section title and deliverable questions.

    Args:
        html: The HTML content of a lab section.
        section_number: The section number (1-based).

    Returns:
        A Section object with extracted questions.
    """
    soup = BeautifulSoup(html, "lxml")

    # Find all google-codelab-step elements
    steps = soup.find_all("google-codelab-step")

    # Get the specific step by index (section_number is 1-based)
    step_index = section_number - 1
    if step_index < len(steps):
        step_content = steps[step_index]
        section_title = step_content.get("label", "")
    else:
        # Fallback to looking for div.instructions or similar
        step_content = (
            soup.find("div", class_="instructions")
            or soup.find("div", class_="step")
            or soup
        )
        section_title = ""
        title_elem = step_content.find("h1") or step_content.find("h2")
        if title_elem:
            section_title = title_elem.get_text(strip=True)
            # Remove leading number if present
            title_match = re.match(r"^\d+\.\s*(.+)$", section_title)
            if title_match:
                section_title = title_match.group(1)

    # Extract deliverable bullet points
    questions = extract_deliverable_questions(step_content)

    return Section(
        number=section_number,
        title=section_title,
        questions=questions,
        url_hash=f"#{section_number - 1}",
    )


def extract_deliverable_questions(soup: BeautifulSoup) -> list[Question]:
    """
    Extract ONLY bold bullet points from section content.

    On the GenSec lab website, deliverable tasks are marked with bold text
    inside bullet points. This function extracts only those items.

    Args:
        soup: BeautifulSoup object of the section content.

    Returns:
        A list of Question objects representing deliverables.
    """
    questions = []

    # Find all list items
    for li in soup.find_all("li"):
        # Skip if inside a code block
        if li.find_parent("pre") or li.find_parent("code"):
            continue

        # Check if the li contains bold text (strong or b tag)
        bold_elem = li.find("strong") or li.find("b")

        if bold_elem:
            # Get the text from the bold element
            text = bold_elem.get_text(strip=True)
            if text:
                question = Question(
                    text=text,
                    requires_screenshot=False,
                    requires_odinid=False,
                )
                questions.append(question)

    return questions


def get_section_count(html: str) -> int:
    """
    Determine the number of sections in a lab page.

    Args:
        html: The HTML content of a lab page.

    Returns:
        The number of sections found.
    """
    soup = BeautifulSoup(html, "lxml")

    # First try: count google-codelab-step elements (most common)
    codelab_steps = soup.find_all("google-codelab-step")
    if codelab_steps:
        return len(codelab_steps)

    # Alternative: count step elements in navigation
    steps = soup.find_all("li", class_="step") or soup.find_all("a", class_="step")
    if steps:
        return len(steps)

    # Fallback: count by looking at navigation links
    nav = soup.find("div", id="drawer") or soup.find("nav")
    if nav:
        links = nav.find_all("a", href=True)
        hash_links = [l for l in links if l.get("href", "").startswith("#")]
        if hash_links:
            return len(hash_links)

    return 0
