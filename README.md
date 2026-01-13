# Lab Template Generator

A CLI tool that automates the tedious task of creating lab report templates from course websites.

## Why I Built This

I was spending too much time on repetitive documentation work - copying section titles, formatting bullet points, setting up document structure. This is busywork that doesn't help me learn anything new.

So I automated it. This tool scrapes lab content from a course website and generates ready-to-use templates, letting me focus on the actual learning instead of formatting documents.

**Built with Claude Code** as a learning exercise in AI-assisted development.

## How It Works

- **Web scraping** - Parses HTML from course lab pages
- **Smart extraction** - Pulls only deliverable items (bold bullet points)
- **Local caching** - Avoids repeated network requests (24-hour cache)
- **Multiple formats** - Outputs `.docx` (Word/Google Docs) or `.md` (Markdown)

No API keys or external services required. Pure Python CLI tool.

## Requirements

- Python 3.10+
- Internet connection (first run only, then cached)

## Installation

```bash
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator
./install.sh
source .venv/bin/activate
```

Or manually:

```bash
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator
python3 -m venv .venv && source .venv/bin/activate
pip install .
```

## Usage

```bash
# List all available labs
gensec-template list

# Generate template for a specific lab
gensec-template generate 06.1

# Generate as Markdown
gensec-template generate 06.1 --format md

# Generate all labs for a week
gensec-template generate-week 01

# Clear cache
gensec-template clear-cache
```

## Output Example

```markdown
# 06.1: Code Generation

## 2. Exercise #1
- First deliverable task from the lab
- Second deliverable task
- Third deliverable task

## 3. Exercise #2
- Another set of tasks to complete
- More items extracted from bold bullets
```

## Project Structure

```
src/gensec_template/
├── cli.py        # Command-line interface (Typer)
├── scraper.py    # Web scraping (httpx)
├── parser.py     # HTML parsing (BeautifulSoup)
├── generator.py  # Document generation (python-docx)
├── cache.py      # Local caching (diskcache)
└── models.py     # Data models (dataclasses)
```

## Customization

To adapt this for a different course website:
1. Update `BASE_URL` in `scraper.py`
2. Modify `parser.py` to match the HTML structure of your target site
3. Adjust extraction logic in `extract_deliverable_questions()`

## License

MIT
