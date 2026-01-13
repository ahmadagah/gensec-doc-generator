# Lab Template Generator

A CLI tool that automates creating lab report templates from course websites.

## Why I Built This

I was spending too much time on repetitive documentation work - copying section titles, formatting bullet points, setting up document structure. This is busywork that doesn't help me learn.

So I automated it. This tool scrapes lab content and generates ready-to-use templates, letting me focus on actual learning.

**Built with Claude Code** as a learning exercise in AI-assisted development.

## How It Works

1. Fetches the course index page to discover all available labs
2. For each lab, parses the HTML structure (Google Codelab format)
3. Extracts only **bold bullet points** - these are the deliverable tasks
4. Generates a clean `.docx` or `.md` template

No API keys required. Pure Python CLI tool with local caching.

## Requirements

- Python 3.10+
- Internet connection (first run, then cached for 24 hours)

## Installation

```bash
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator
./install.sh
source .venv/bin/activate
```

## Usage

```bash
# List all available labs
gensec-template list

# Generate template for a specific lab
gensec-template generate 04.1

# Generate as Markdown
gensec-template generate 04.1 --format md

# Generate all labs for a week
gensec-template generate-week 06

# Generate everything
gensec-template generate-all

# Clear cache (force fresh fetch)
gensec-template clear-cache
```

## Output Example

```markdown
# 06.1: Code Generation

## 2. Exercise #1: Code generation
- Ask an LLM to generate a prompt that can produce the code above
- Then, in a new chat, send the prompt to the LLM...
- Handcraft a prompt that allows an LLM to generate code...

## 3. Exercise #2: Unit tests
- Ask an LLM to instrument the password program...
- Do the unit tests generated provide sufficient coverage?
```

## Configuration (Optional)

The default source URL is `https://codelabs.cs.pdx.edu/cs475/` - no configuration needed for standard use.

To use a **different** course website:

```bash
# Option 1: CLI flag (one-time)
gensec-template --url "https://other-site.edu/labs/" list

# Option 2: Environment variable
export LAB_TEMPLATE_URL="https://other-site.edu/labs/"

# Option 3: Config file (persistent)
gensec-template config set "https://other-site.edu/labs/"

# View current config
gensec-template config show

# Reset to default
gensec-template config reset
```

## Adapting for Other Sites

If targeting a site with different HTML structure:

1. Modify `parser.py`:
   - `parse_lab_index_html()` - for the lab listing page
   - `parse_lab_section_html()` - for individual lab pages
   - `extract_deliverable_questions()` - for content extraction

2. Clear cache after changes:
   ```bash
   gensec-template clear-cache
   ```

## Project Structure

```
src/gensec_template/
├── cli.py        # Command-line interface (Typer)
├── config.py     # URL configuration management
├── scraper.py    # Web scraping (httpx)
├── parser.py     # HTML parsing (BeautifulSoup)
├── generator.py  # Document generation (python-docx)
├── cache.py      # Local caching (diskcache)
└── models.py     # Data models
```

## License

MIT
