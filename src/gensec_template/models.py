"""
Data models for the lab template CLI tool.

This module defines the core data structures used throughout the application
for representing labs, sections, and questions scraped from course websites.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json
from datetime import datetime


@dataclass
class Question:
    """
    A bullet-point question/task from a lab section.

    Represents an individual task or question that students need to complete
    as part of a lab section. Tracks whether the question requires a screenshot
    or OdinId to be included in the response.

    Attributes:
        text: The full text of the question or task.
        requires_screenshot: True if the question mentions "screenshot",
            indicating a screenshot should be included in the answer.
        requires_odinid: True if the question mentions "OdinId",
            indicating the student's OdinId should be included.
    """
    text: str
    requires_screenshot: bool = False
    requires_odinid: bool = False

    @classmethod
    def from_text(cls, text: str) -> "Question":
        """
        Factory method to create a Question from raw text.

        Automatically detects if the question requires a screenshot or OdinId
        based on the presence of those keywords in the text.

        Args:
            text: The raw question text.

        Returns:
            A new Question instance with appropriate flags set.
        """
        text_lower = text.lower()
        return cls(
            text=text.strip(),
            requires_screenshot="screenshot" in text_lower,
            requires_odinid="odinid" in text_lower or "odin id" in text_lower
        )

    def to_dict(self) -> dict:
        """Convert the Question to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """Create a Question from a dictionary."""
        return cls(
            text=data["text"],
            requires_screenshot=data.get("requires_screenshot", False),
            requires_odinid=data.get("requires_odinid", False)
        )


@dataclass
class Section:
    """
    A section within a lab.

    Represents a numbered section within a lab document, containing
    one or more questions or tasks for students to complete.

    Attributes:
        number: The section number (1, 2, 3, ...).
        title: The section title (e.g., "Models via APIs").
        questions: List of Question objects in this section.
        url_hash: The URL hash anchor for direct linking (e.g., "#0", "#1").
    """
    number: int
    title: str
    questions: list[Question] = field(default_factory=list)
    url_hash: str = ""

    @property
    def question_count(self) -> int:
        """Return the number of questions in this section."""
        return len(self.questions)

    @property
    def screenshot_count(self) -> int:
        """Return the number of questions requiring screenshots."""
        return sum(1 for q in self.questions if q.requires_screenshot)

    @property
    def odinid_count(self) -> int:
        """Return the number of questions requiring OdinId."""
        return sum(1 for q in self.questions if q.requires_odinid)

    def add_question(self, question: Question) -> None:
        """Add a question to this section."""
        self.questions.append(question)

    def add_question_from_text(self, text: str) -> Question:
        """
        Create and add a question from raw text.

        Args:
            text: The raw question text.

        Returns:
            The newly created Question instance.
        """
        question = Question.from_text(text)
        self.questions.append(question)
        return question

    def to_dict(self) -> dict:
        """Convert the Section to a dictionary."""
        return {
            "number": self.number,
            "title": self.title,
            "questions": [q.to_dict() for q in self.questions],
            "url_hash": self.url_hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Section":
        """Create a Section from a dictionary."""
        return cls(
            number=data["number"],
            title=data["title"],
            questions=[Question.from_dict(q) for q in data.get("questions", [])],
            url_hash=data.get("url_hash", "")
        )


@dataclass
class Lab:
    """
    A complete lab with all its sections.

    Represents a full lab document containing multiple sections,
    each with their own questions and tasks.

    Attributes:
        number: The lab number (e.g., "01.3").
        lab_id: The unique lab identifier (e.g., "G01.3_ProgramModel").
        title: The lab title (e.g., "Programmatic Model Access").
        url: The full URL to the lab page.
        sections: List of Section objects in this lab.
        duration_minutes: Estimated time to complete the lab in minutes.
        description: Optional description of the lab content.
    """
    number: str
    lab_id: str
    title: str
    url: str
    sections: list[Section] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    description: Optional[str] = None

    @property
    def section_count(self) -> int:
        """Return the number of sections in this lab."""
        return len(self.sections)

    @property
    def total_questions(self) -> int:
        """Return the total number of questions across all sections."""
        return sum(s.question_count for s in self.sections)

    @property
    def total_screenshots(self) -> int:
        """Return the total number of questions requiring screenshots."""
        return sum(s.screenshot_count for s in self.sections)

    @property
    def total_odinids(self) -> int:
        """Return the total number of questions requiring OdinId."""
        return sum(s.odinid_count for s in self.sections)

    def get_section(self, number: int) -> Optional[Section]:
        """
        Get a section by its number.

        Args:
            number: The section number to find.

        Returns:
            The Section if found, None otherwise.
        """
        for section in self.sections:
            if section.number == number:
                return section
        return None

    def add_section(self, section: Section) -> None:
        """Add a section to this lab."""
        self.sections.append(section)

    def get_section_url(self, section: Section) -> str:
        """
        Get the full URL to a specific section.

        Args:
            section: The section to get the URL for.

        Returns:
            The full URL including the hash anchor.
        """
        if section.url_hash:
            return f"{self.url}{section.url_hash}"
        return self.url

    def to_dict(self) -> dict:
        """Convert the Lab to a dictionary."""
        return {
            "number": self.number,
            "lab_id": self.lab_id,
            "title": self.title,
            "url": self.url,
            "sections": [s.to_dict() for s in self.sections],
            "duration_minutes": self.duration_minutes,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Lab":
        """Create a Lab from a dictionary."""
        return cls(
            number=data["number"],
            lab_id=data["lab_id"],
            title=data["title"],
            url=data["url"],
            sections=[Section.from_dict(s) for s in data.get("sections", [])],
            duration_minutes=data.get("duration_minutes"),
            description=data.get("description")
        )

    def to_json(self, indent: int = 2) -> str:
        """
        Serialize the Lab to a JSON string.

        Args:
            indent: Number of spaces for indentation.

        Returns:
            JSON string representation of the lab.
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "Lab":
        """
        Create a Lab from a JSON string.

        Args:
            json_str: JSON string representation of a lab.

        Returns:
            A new Lab instance.
        """
        return cls.from_dict(json.loads(json_str))


@dataclass
class LabIndex:
    """
    Index of all available labs.

    Maintains a collection of all labs scraped from the documentation,
    along with metadata about when the scrape occurred.

    Attributes:
        labs: List of all Lab objects.
        last_updated: ISO timestamp of the last scrape.
    """
    labs: list[Lab] = field(default_factory=list)
    last_updated: str = ""

    def __post_init__(self):
        """Set default last_updated if not provided."""
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

    @property
    def lab_count(self) -> int:
        """Return the number of labs in the index."""
        return len(self.labs)

    @property
    def total_sections(self) -> int:
        """Return the total number of sections across all labs."""
        return sum(lab.section_count for lab in self.labs)

    @property
    def total_questions(self) -> int:
        """Return the total number of questions across all labs."""
        return sum(lab.total_questions for lab in self.labs)

    def get_lab_by_number(self, number: str) -> Optional[Lab]:
        """
        Get a lab by its number.

        Args:
            number: The lab number to find (e.g., "01.3").

        Returns:
            The Lab if found, None otherwise.
        """
        for lab in self.labs:
            if lab.number == number:
                return lab
        return None

    def get_lab_by_id(self, lab_id: str) -> Optional[Lab]:
        """
        Get a lab by its ID.

        Args:
            lab_id: The lab ID to find (e.g., "G01.3_ProgramModel").

        Returns:
            The Lab if found, None otherwise.
        """
        for lab in self.labs:
            if lab.lab_id == lab_id:
                return lab
        return None

    def add_lab(self, lab: Lab) -> None:
        """Add a lab to the index."""
        self.labs.append(lab)
        self.last_updated = datetime.now().isoformat()

    def get_labs_sorted(self, by: str = "number") -> list[Lab]:
        """
        Get labs sorted by a specified field.

        Args:
            by: Field to sort by ("number", "title", or "lab_id").

        Returns:
            Sorted list of labs.
        """
        if by == "number":
            return sorted(self.labs, key=lambda x: x.number)
        elif by == "title":
            return sorted(self.labs, key=lambda x: x.title)
        elif by == "lab_id":
            return sorted(self.labs, key=lambda x: x.lab_id)
        return self.labs

    def to_dict(self) -> dict:
        """Convert the LabIndex to a dictionary."""
        return {
            "labs": [lab.to_dict() for lab in self.labs],
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LabIndex":
        """Create a LabIndex from a dictionary."""
        return cls(
            labs=[Lab.from_dict(lab) for lab in data.get("labs", [])],
            last_updated=data.get("last_updated", "")
        )

    def to_json(self, indent: int = 2) -> str:
        """
        Serialize the LabIndex to a JSON string.

        Args:
            indent: Number of spaces for indentation.

        Returns:
            JSON string representation of the index.
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "LabIndex":
        """
        Create a LabIndex from a JSON string.

        Args:
            json_str: JSON string representation of a lab index.

        Returns:
            A new LabIndex instance.
        """
        return cls.from_dict(json.loads(json_str))

    def save_to_file(self, filepath: str) -> None:
        """
        Save the LabIndex to a JSON file.

        Args:
            filepath: Path to the output file.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filepath: str) -> "LabIndex":
        """
        Load a LabIndex from a JSON file.

        Args:
            filepath: Path to the input file.

        Returns:
            A new LabIndex instance.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())
