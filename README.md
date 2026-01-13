# Lab Template Generator

A CLI tool that automates creating lab report templates from course websites.

## Why I Built This

I was spending too much time on repetitive documentation work - copying section titles, formatting bullet points, setting up document structure. This is busywork that doesn't help me learn.

So I automated it. This tool scrapes lab content and generates ready-to-use templates, letting me focus on actual learning.

**Built with Claude Code** as a learning exercise in AI-assisted development.

## How It Works

- **Web scraping** - Parses HTML from course lab pages
- **Smart extraction** - Pulls only deliverable items (bold bullet points)
- **Local caching** - Avoids repeated requests (24-hour cache)
- **Dynamic configuration** - Change source URL without modifying code

No API keys required. Pure Python CLI tool.

## Requirements

- Python 3.10+
- Internet connection (first run, then cached)

## Installation

```bash
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator
./install.sh
source .venv/bin/activate
```

## Configuration

The source URL can be configured in multiple ways (highest to lowest priority):

### 1. CLI Flag
```bash
gensec-template --url "https://example.com/labs/" list
gensec-template -u "https://example.com/labs/" generate 01.1
```

### 2. Environment Variable
```bash
export LAB_TEMPLATE_URL="https://example.com/labs/"
gensec-template list
```

### 3. Config File
```bash
# Save URL to config file
gensec-template config set "https://example.com/labs/"

# View current configuration
gensec-template config show

# Reset to default
gensec-template config reset
```

Config file location: `~/.config/gensec-template/config.json`

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

# Generate everything
gensec-template generate-all

# Clear cache (force fresh fetch)
gensec-template clear-cache

# View cache info
gensec-template cache-info
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
├── config.py     # Configuration management
├── scraper.py    # Web scraping (httpx)
├── parser.py     # HTML parsing (BeautifulSoup)
├── generator.py  # Document generation (python-docx)
├── cache.py      # Local caching (diskcache)
└── models.py     # Data models (dataclasses)
```

## Adapting for Other Sites

1. Set your URL:
   ```bash
   gensec-template config set "https://your-course-site.edu/labs/"
   ```

2. If the HTML structure differs, modify `parser.py`:
   - Update `parse_lab_index_html()` for the lab listing page
   - Update `parse_lab_section_html()` for individual lab pages
   - Adjust `extract_deliverable_questions()` for content extraction

3. Clear cache after changes:
   ```bash
   gensec-template clear-cache
   ```

## License

MIT
