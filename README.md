# GenSec Lab Template Generator

A standalone CLI tool that generates lab templates for **CS 475/575 Generative Security** at Portland State University.

## How It Works

- **Live scraping** - Fetches content directly from the [course website](https://codelabs.cs.pdx.edu/cs475/)
- **Local caching** - Cached for 24 hours to avoid repeated requests
- **No API keys** - No environment variables or external services required
- **Offline-capable** - Works offline if content is already cached

This is a pure Python CLI tool. No AI agents, cloud services, or external APIs needed.

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

Or manually with pip/uv/conda:

```bash
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator
python3 -m venv .venv && source .venv/bin/activate
pip install .
```

## Usage

```bash
# List all labs
gensec-template list

# Generate template for a lab
gensec-template generate 06.1

# Generate as Markdown
gensec-template generate 06.1 --format md

# Generate all labs for a week
gensec-template generate-week 01

# Generate everything
gensec-template generate-all

# Clear cache (force fresh fetch)
gensec-template clear-cache
```

## Output

Generates `.docx` (Google Docs compatible) or `.md` files with:
- Lab title as main heading
- Section titles as subheadings
- Only the **bold bullet points** (deliverable tasks)

```markdown
# 06.1: Code Generation

## 2. Exercise #1: Code generation
- Ask an LLM to generate a prompt that can produce the code above
- Then, in a new chat, send the prompt to the LLM...
- Handcraft a prompt that allows an LLM to generate code...

## 3. Exercise #2: Unit tests
- Ask an LLM to instrument the password program...
- Do the unit tests generated provide sufficient coverage?
- Run the generated program and analyze the results
```

## Troubleshooting

**Command not found**: Activate the virtual environment first
```bash
source .venv/bin/activate
```

**Stale content**: Clear the cache
```bash
gensec-template clear-cache
```

## License

MIT
