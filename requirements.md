# Gen-Sec Lab Template Generator

## Project Overview

A command-line tool that automatically generates Google Docs-compatible templates for CS 475/575 Generative Security Application Engineering lab assignments. The tool scrapes the lab website, extracts **ONLY the bullet-point deliverables** (questions/tasks requiring student response), and generates a clean `.docx` document with proper heading hierarchy ready for students to fill in their answers.

## Problem Statement

Students taking the CS 475/575 course at Portland State University must:
1. Read through each lab's multiple sections on the website
2. Manually identify bullet-point questions/tasks that require answers or screenshots
3. Create a Google Doc with proper heading hierarchy for each question
4. Fill in their answers under each question

This manual process is time-consuming and error-prone. The tool automates steps 1-3, generating a ready-to-use template.

**Key Requirement**: The generated document should contain **ONLY**:
- Lab title as Heading 1
- Section titles as Heading 2
- Bullet points (deliverables/questions) under each section
- Space for answers

The document should **NOT** include instructional text, code snippets, or explanations from the lab - only the actionable bullet points that students need to respond to.

## Target Website

- **Main Course Page**: `https://codelabs.cs.pdx.edu/cs475/`
- **Individual Lab URL Pattern**: `https://codelabs.cs.pdx.edu/labs/{LAB_ID}/index.html?index=..%2F..cs475#0`
- **Section Navigation**: Hash anchors (`#0`, `#1`, `#2`, etc.) for each section within a lab

## Lab Structure Analysis

### Course Labs Discovered

| Lab Number | Lab ID | Title |
|------------|--------|-------|
| 01.1 | G01.1_Setup | Setup |
| 01.2 | G01.2_Ollama | Ollama |
| 01.3 | G01.3_ProgramModel | Programmatic Model Access |
| 01.4 | G01.4_ModelTesting | Model Stress Testing |
| 02.1 | G02.1_LangChainTour | LangChain Tour |
| 02.2 | G02.2_LangChainDocumentLoading | LangChain Documents |
| 02.3 | G02.3_LangChainRAG | LangChain RAG Application |
| 02.4 | G02.4_hw1 | Homework #1 |
| 03.1 | G03.1_LangChainAgents | LangChain Agents |
| 03.2 | G03.2_hw2 | Homework #2 |
| 04.1 | G04.1_SecuringGenerativeApps | Securing LLM Applications |
| 04.2 | G04.2_hw3 | Homework #3 |
| 05.1 | G05.1_CodeSummarization | Code Documentation and Summarization |
| 05.2 | G05.2_CodeAnalysis | Code Analysis |
| 05.3 | G05.3_hw4 | Homework #4 |
| 06.1 | G06.1_VulnerabilitiesExploitation | Vulnerabilities and Exploitation |
| 06.2 | G06.2_VulnerabilityTools | Vulnerability Tools |
| 06.3 | G06.3_hw5 | Homework #5 |
| 07.1 | G07.1_CommandGeneration | Commands and Configurations |
| 07.2 | G07.2_CommandAgents | Command Agents |
| 07.3 | G07.3_hw6 | Homework #6 |
| 08.1 | G08.1_CodeGeneration | Code Generation |
| 08.2 | G08.2_CodeAgents | Coding Agents |
| 08.3 | G08.3_hw7 | Homework #7 |
| 09.1 | G09.1_ThreatIntelligence | Threat Intelligence |
| 09.2 | G09.2_final | Final Project |
| 10.1 | G10.1_SocialEngineering | Social Engineering |

### HTML Structure Pattern

Each lab page follows a consistent structure:

```
Lab Page (index.html)
├── Header: Lab title (e.g., "01.3: Programmatic Model Access")
├── Left Sidebar: Section navigation (numbered tabs: 1, 2, 3, ...)
│   ├── Section 1: "Models via APIs" → accessed via #0
│   ├── Section 2: "Ollama" → accessed via #1
│   └── Section 3: "Model laboratory" → accessed via #2
└── Content Area: Section content (changes based on #hash)
    ├── Section number and heading (e.g., "3. Model laboratory")
    ├── Instructional text (DO NOT EXTRACT)
    ├── Code blocks (DO NOT EXTRACT)
    └── Bullet point questions/tasks (EXTRACT THESE ONLY)
```

**CRITICAL**: Only extract `<li>` elements that are actual deliverables - tasks requiring student action like screenshots, explanations, or submissions. Ignore bullet points that are part of instructions or explanations.

### Output Document Structure

The generated `.docx` should have a **clean, minimal structure**:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  01.3: Programmatic Model Access                     [H1]   │
│                                                             │
│  1. Models via APIs                                  [H2]   │
│  • Take a screenshot of the results for one of the         │
│    prompts that includes your OdinId                       │
│                                                             │
│  [Answer:]                                                  │
│                                                             │
│                                                             │
│  2. Ollama                                           [H2]   │
│  • Take a screenshot of the results for one of the         │
│    prompts that includes your OdinId                       │
│                                                             │
│  [Answer:]                                                  │
│                                                             │
│                                                             │
│  3. Model laboratory                                 [H2]   │
│  • Take a screenshot of the results for one of the         │
│    prompts that includes your OdinId                       │
│                                                             │
│  [Answer:]                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Document Rules**:
1. **Heading 1** (24pt, Bold): Lab number and title (e.g., "01.3: Programmatic Model Access")
2. **Heading 2** (18pt, Bold): Section number and title (e.g., "1. Models via APIs")
3. **Bullet List**: Only the deliverable bullet points - nothing else
4. **Answer Space**: Empty paragraph(s) for student response after each bullet point
5. **No extra content**: No instructional text, no code blocks, no explanations

## Functional Requirements

### FR-1: Lab Discovery
- Scrape the main course page (`https://codelabs.cs.pdx.edu/cs475/`)
- Extract all available labs with their:
  - Lab number (e.g., "01.3")
  - Lab ID (e.g., "G01.3_ProgramModel")
  - Title (e.g., "Programmatic Model Access")
  - URL path (e.g., "/labs/G01.3_ProgramModel/index.html?index=..%2F..cs475")
- Cache the lab list locally for faster subsequent access

### FR-2: Lab Structure Parsing
Given a lab URL or lab ID:
- Fetch the lab page HTML
- Extract the main lab title from the page header (e.g., "01.3: Programmatic Model Access")
- Extract all section titles from the left sidebar navigation (numbered 1, 2, 3, ...)
- For each section (iterate through hash anchors #0, #1, #2, ...):
  - Fetch the section content
  - Extract the section number and title (e.g., "3. Model laboratory")
  - **Identify ONLY deliverable bullet points** - tasks requiring student action

**Bullet Point Extraction Rules**:
- Extract `<li>` elements that contain action verbs indicating a deliverable:
  - `"Take a screenshot..."` - requires screenshot submission
  - `"Submit..."` - requires submission
  - `"Demonstrate..."` - requires demonstration
  - `"Explain..."` - requires written explanation
  - `"Show..."` - requires showing results
  - `"Include..."` - requires including something in submission
  - `"Provide..."` - requires providing information
  - `"Document..."` - requires documentation
  - `"Answer..."` - requires answering a question
- **DO NOT extract**:
  - Bullet points that are part of instructions (e.g., "Edit the file to...")
  - Bullet points that are navigation or setup steps
  - Bullet points within code examples
- Look for bullet points that mention "OdinId" as these are often key deliverables

### FR-3: Document Generation
Generate a Microsoft Word document (`.docx`) containing:
- **Heading 1**: Lab number and title (e.g., "01.3: Programmatic Model Access")
- For each section:
  - **Heading 2**: Section number and title (e.g., "1. Models via APIs")
  - **Bullet list**: All questions/tasks from that section
  - **Empty paragraph**: Space for student to add answers

### FR-4: Table of Contents
The document should include a clickable table of contents at the top that:
- Lists all Heading 1 entries (lab titles)
- Lists all Heading 2 entries (sections)
- Allows clicking to navigate to that section (Google Docs compatible)

### FR-5: Command-Line Interface
```bash
# List all available labs
gensec-template list

# Generate template for a specific lab by number
gensec-template generate 01.3

# Generate template for a specific lab by ID
gensec-template generate G01.3_ProgramModel

# Generate template for a specific lab by URL
gensec-template generate "https://codelabs.cs.pdx.edu/labs/G01.3_ProgramModel/index.html"

# Generate templates for a week's labs (e.g., all 01.x labs)
gensec-template generate-week 01

# Output to specific file
gensec-template generate 01.3 --output ~/Documents/lab_01.3_template.docx

# Generate all labs at once
gensec-template generate-all --output-dir ~/Documents/gensec/
```

### FR-6: Multiple Output Formats (Optional Enhancement)
- Primary: `.docx` (Microsoft Word, Google Docs compatible)
- Secondary: `.md` (Markdown)
- Tertiary: `.html` (viewable in browser)

## Non-Functional Requirements

### NFR-1: Performance
- Lab list scraping should complete within 5 seconds
- Individual lab template generation should complete within 10 seconds
- Use caching to avoid redundant web requests

### NFR-2: Reliability
- Handle network errors gracefully with retry logic (3 attempts)
- Validate lab URLs before processing
- Provide clear error messages for invalid inputs

### NFR-3: Compatibility
- Generated `.docx` files must be compatible with:
  - Google Docs (upload and maintain formatting)
  - Microsoft Word (2016+)
  - LibreOffice Writer
- Python 3.10+ compatibility

### NFR-4: Usability
- Clear CLI help messages
- Progress indicators for long operations
- Color-coded output (success/error/warning)

## Technical Architecture

### Technology Stack
- **Language**: Python 3.10+
- **HTTP Client**: `httpx` or `requests` (for web scraping)
- **HTML Parsing**: `beautifulsoup4` with `lxml` parser
- **Document Generation**: `python-docx` (for .docx files)
- **CLI Framework**: `typer` or `click`
- **Caching**: `diskcache` or simple JSON file cache
- **Package Manager**: `uv` (preferred) or `pip`

### Project Structure
```
gensec-lab-template-generator/
├── pyproject.toml                 # Project metadata and dependencies
├── README.md                      # User documentation
├── requirements.md                # This file
├── src/
│   └── gensec_template/
│       ├── __init__.py
│       ├── __main__.py           # CLI entry point
│       ├── cli.py                # Command-line interface
│       ├── scraper.py            # Web scraping logic
│       ├── parser.py             # HTML parsing and structure extraction
│       ├── generator.py          # Document generation
│       ├── models.py             # Data models (Lab, Section, Question)
│       └── cache.py              # Caching utilities
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_parser.py
│   └── test_generator.py
└── output/                        # Default output directory for generated docs
```

### Data Models

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Question:
    """A bullet-point question/task from a lab section."""
    text: str                      # The question text
    requires_screenshot: bool      # True if mentions "screenshot"
    requires_odinid: bool          # True if mentions "OdinId"

@dataclass
class Section:
    """A section within a lab."""
    number: int                    # Section number (1, 2, 3, ...)
    title: str                     # Section title (e.g., "Models via APIs")
    questions: list[Question]      # List of questions/tasks in this section
    url_hash: str                  # Hash anchor (e.g., "#0", "#1")

@dataclass
class Lab:
    """A complete lab with all its sections."""
    number: str                    # Lab number (e.g., "01.3")
    lab_id: str                    # Lab ID (e.g., "G01.3_ProgramModel")
    title: str                     # Lab title (e.g., "Programmatic Model Access")
    url: str                       # Full URL to the lab
    sections: list[Section]        # List of all sections
    duration_minutes: Optional[int] # Estimated duration
    description: Optional[str]     # Lab description

@dataclass
class LabIndex:
    """Index of all available labs."""
    labs: list[Lab]
    last_updated: str              # ISO timestamp of last scrape
```

### Scraping Logic

```python
# Pseudocode for lab scraping

def scrape_lab_index(base_url: str) -> LabIndex:
    """Scrape the main course page to get all available labs."""
    response = fetch(base_url)
    soup = parse_html(response.text)

    labs = []
    for card in soup.find_all(class_="codelab-card"):
        lab = Lab(
            number=extract_lab_number(card),
            lab_id=extract_lab_id(card),
            title=extract_title(card),
            url=build_lab_url(card),
            sections=[],  # Populated later
            duration_minutes=extract_duration(card),
            description=extract_description(card)
        )
        labs.append(lab)

    return LabIndex(labs=labs, last_updated=now())

def scrape_lab_sections(lab: Lab) -> Lab:
    """Scrape all sections from a specific lab."""
    # First, get the number of sections from sidebar
    response = fetch(lab.url + "#0")
    soup = parse_html(response.text)

    section_links = soup.find_all(class_="step")  # Or similar selector
    num_sections = len(section_links)

    sections = []
    for i in range(num_sections):
        section_url = f"{lab.url}#{i}"
        response = fetch(section_url)
        soup = parse_html(response.text)

        section = Section(
            number=i + 1,
            title=extract_section_title(soup),
            questions=extract_questions(soup),
            url_hash=f"#{i}"
        )
        sections.append(section)

    lab.sections = sections
    return lab

def extract_questions(soup) -> list[Question]:
    """Extract ONLY deliverable bullet-points from section content.

    IMPORTANT: Only extract bullet points that are actual deliverables
    requiring student action. Ignore instructional bullet points.
    """
    questions = []

    # Action verbs that indicate a deliverable (must appear at START of bullet)
    deliverable_starters = [
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
    ]

    # Words that indicate NOT a deliverable (instructional)
    exclusion_indicators = [
        "edit the file",
        "run the command",
        "install",
        "navigate to",
        "click on",
        "open the",
        "create a",
        "copy the",
    ]

    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        lower_text = text.lower()

        # Skip if it matches exclusion patterns (instructions)
        if any(excl in lower_text for excl in exclusion_indicators):
            continue

        # Check if this starts with a deliverable action verb
        is_deliverable = any(lower_text.startswith(starter) for starter in deliverable_starters)

        # Also check for OdinId mentions - these are almost always deliverables
        has_odinid = "odinid" in lower_text or "odin id" in lower_text

        if is_deliverable or has_odinid:
            question = Question(
                text=text,
                requires_screenshot="screenshot" in lower_text,
                requires_odinid=has_odinid
            )
            questions.append(question)

    return questions
```

### Document Generation Logic

```python
# Pseudocode for document generation

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def generate_docx(lab: Lab, output_path: str):
    """Generate a .docx template for the given lab."""
    doc = Document()

    # Set up styles
    setup_styles(doc)

    # Add title page (optional)
    add_title_page(doc, lab)

    # Add table of contents placeholder
    add_toc_placeholder(doc)

    # Add main lab heading (H1)
    doc.add_heading(f"{lab.number}: {lab.title}", level=1)

    # Add each section
    for section in lab.sections:
        # Add section heading (H2)
        doc.add_heading(f"{section.number}. {section.title}", level=2)

        # Add questions as bullet list
        for question in section.questions:
            para = doc.add_paragraph(style='List Bullet')
            para.add_run(question.text)

            # Add indicator if screenshot required
            if question.requires_screenshot:
                para.add_run(" [Screenshot Required]").italic = True

        # Add empty space for answers
        doc.add_paragraph()  # Empty line for answer
        doc.add_paragraph()  # Additional spacing

    # Save document
    doc.save(output_path)

def setup_styles(doc):
    """Configure document styles for Google Docs compatibility."""
    styles = doc.styles

    # Heading 1 style
    h1 = styles['Heading 1']
    h1.font.size = Pt(24)
    h1.font.bold = True

    # Heading 2 style
    h2 = styles['Heading 2']
    h2.font.size = Pt(18)
    h2.font.bold = True

    # Normal text style
    normal = styles['Normal']
    normal.font.size = Pt(11)
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. Set up project structure with `pyproject.toml`
2. Implement data models (`models.py`)
3. Implement basic HTTP client with retry logic
4. Create caching layer for scraped data

### Phase 2: Web Scraping
1. Implement lab index scraping from main page
2. Implement individual lab section scraping
3. Implement question extraction from section content
4. Add error handling and validation

### Phase 3: Document Generation
1. Implement basic `.docx` generation with `python-docx`
2. Add proper heading styles (H1, H2)
3. Add bullet point formatting for questions
4. Add table of contents generation

### Phase 4: CLI Interface
1. Implement `list` command to show available labs
2. Implement `generate` command for single lab
3. Implement `generate-week` command for multiple labs
4. Add output file path options
5. Add progress indicators and colored output

### Phase 5: Polish and Testing
1. Write unit tests for each module
2. Add integration tests with mock data
3. Write user documentation (README.md)
4. Test Google Docs compatibility

## Usage Examples

### Example 1: List Available Labs
```bash
$ gensec-template list

CS 475/575: Generative Security Application Engineering
Available Labs:
────────────────────────────────────────────────────────────────
  01.1  Setup                              89 min
  01.2  Ollama                             46 min
  01.3  Programmatic Model Access          11 min
  01.4  Model Stress Testing               36 min
  02.1  LangChain Tour                     21 min
  02.2  LangChain Documents                30 min
  ...

Total: 30 labs
```

### Example 2: Generate Single Lab Template
```bash
$ gensec-template generate 01.3

Fetching lab 01.3: Programmatic Model Access...
Found 3 sections with 3 questions total.
Generating template...

✓ Template saved to: ./output/01.3_Programmatic_Model_Access.docx

Open in Google Docs: Upload file to Google Drive and open with Google Docs
```

### Example 3: Generate Week's Labs
```bash
$ gensec-template generate-week 01

Fetching labs for week 01...
  - 01.1: Setup (14 sections, 12 questions)
  - 01.2: Ollama (5 sections, 4 questions)
  - 01.3: Programmatic Model Access (3 sections, 3 questions)
  - 01.4: Model Stress Testing (4 sections, 6 questions)

Generating templates...
✓ 01.1_Setup.docx
✓ 01.2_Ollama.docx
✓ 01.3_Programmatic_Model_Access.docx
✓ 01.4_Model_Stress_Testing.docx

All templates saved to: ./output/
```

### Example 4: Generated Document Preview
The generated `.docx` file structure:

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Table of Contents                                     │
│  ─────────────────                                     │
│  01.3: Programmatic Model Access                       │
│    1. Models via APIs                                  │
│    2. Ollama                                           │
│    3. Model laboratory                                 │
│                                                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  01.3: Programmatic Model Access                       │
│  ════════════════════════════════                      │
│                                                        │
│  1. Models via APIs                                    │
│  ──────────────────                                    │
│  • Take a screenshot of the results for one of the    │
│    prompts that includes your OdinId                  │
│                                                        │
│  [Your answer/screenshot here]                         │
│                                                        │
│                                                        │
│  2. Ollama                                             │
│  ─────────                                             │
│  • Take a screenshot of the results for one of the    │
│    prompts that includes your OdinId                  │
│                                                        │
│  [Your answer/screenshot here]                         │
│                                                        │
│                                                        │
│  3. Model laboratory                                   │
│  ──────────────────                                    │
│  • Take a screenshot of the results for one of the    │
│    prompts that includes your OdinId                  │
│                                                        │
│  [Your answer/screenshot here]                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Dependencies

```toml
[project]
name = "gensec-lab-template-generator"
version = "0.1.0"
description = "Generate Google Docs templates for CS 475/575 Gen-Sec labs"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27.0",           # HTTP client for web scraping
    "beautifulsoup4>=4.12.0",  # HTML parsing
    "lxml>=5.0.0",             # Fast HTML parser backend
    "python-docx>=1.1.0",      # .docx generation
    "typer>=0.12.0",           # CLI framework
    "rich>=13.0.0",            # Beautiful terminal output
    "diskcache>=5.6.0",        # Persistent caching
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.4.0",
]

[project.scripts]
gensec-template = "gensec_template.__main__:main"
```

## Error Handling

### Expected Errors and Responses

| Error | Cause | Response |
|-------|-------|----------|
| Network timeout | Slow/unavailable server | Retry 3 times, then show error with suggestion to check connection |
| Invalid lab ID | Lab doesn't exist | Show available labs and suggest closest match |
| Parse error | Website structure changed | Show warning, attempt partial extraction, log issue |
| File write error | Permission/disk space | Clear error message with suggested fix |
| No questions found | Section has no deliverables | Include section in doc with note "No deliverables for this section" |

## Future Enhancements

1. **Google Docs API Integration**: Direct upload to Google Drive with sharing permissions
2. **Answer Persistence**: Save answers locally and sync back to document
3. **Progress Tracking**: Track which questions have been answered
4. **Lab Updates Detection**: Notify when a lab's content has changed
5. **Batch Processing**: Generate templates for entire course at once
6. **Custom Styling**: Allow user-defined document themes
7. **Export to PDF**: Direct PDF generation for submission
8. **VS Code Extension**: Integrate with VS Code for seamless workflow

## Acceptance Criteria

1. **Lab Discovery**: Tool can list all 30 labs from the course website
2. **Section Extraction**: Tool correctly identifies all sections for any given lab
3. **Question Detection**: Tool extracts at least 90% of deliverable questions
4. **Document Quality**: Generated `.docx` opens correctly in Google Docs with:
   - Proper heading hierarchy (H1, H2)
   - Working table of contents
   - Bullet-formatted questions
   - Space for answers
5. **CLI Usability**: All commands work as documented
6. **Performance**: Template generation completes within 10 seconds per lab

## Glossary

- **OdinId**: Portland State University student identifier
- **Lab**: A complete assignment module (e.g., "01.3: Programmatic Model Access")
- **Section**: A subsection within a lab (e.g., "1. Models via APIs")
- **Question/Task**: A bullet-point deliverable requiring student response
- **Template**: Pre-formatted document with headings and questions ready for answers
- **Codelab**: Google's format for interactive tutorials (used by the course)
