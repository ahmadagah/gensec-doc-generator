# GenSec Lab Template Generator

A command-line tool that automatically generates Google Docs-compatible templates for **CS 475/575 Generative Security Application Engineering** lab assignments at Portland State University.

## What it does

- Scrapes the [course lab website](https://codelabs.cs.pdx.edu/cs475/)
- Extracts **only the deliverable questions** (tasks requiring your response)
- Generates a clean `.docx` document with proper heading hierarchy
- Ready for you to fill in your answers and screenshots

## Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator

# Run the install script
./install.sh
```

### Manual Install

Works with **pip**, **uv**, **conda**, or any Python environment:

```bash
# Clone the repository
git clone https://github.com/ahmadagah/gensec-doc-generator.git
cd gensec-doc-generator

# Create a virtual environment (choose one)
python3 -m venv .venv          # Standard Python
# OR
uv venv                         # Using uv
# OR
conda create -n gensec python=3.10  # Using conda

# Activate it
source .venv/bin/activate       # Linux/macOS
# OR
.venv\Scripts\activate          # Windows
# OR
conda activate gensec           # Conda

# Install the package
pip install .
```

## Usage

### List all available labs

```bash
gensec-template list
```

Output:
```
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Number ┃ Title                        ┃ Duration ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 01.1   │ Setup                        │   83 min │
│ 01.2   │ Ollama                       │   46 min │
│ 01.3   │ Programmatic Model Access    │   11 min │
│ ...    │ ...                          │      ... │
└────────┴──────────────────────────────┴──────────┘
```

### Generate a template for a specific lab

```bash
# By lab number
gensec-template generate 01.3

# Specify output file
gensec-template generate 01.3 --output ~/Documents/lab01.3.docx

# Generate as Markdown instead
gensec-template generate 01.3 --format md
```

### Generate templates for a week's labs

```bash
# Generate all 01.x labs
gensec-template generate-week 01

# Custom output directory
gensec-template generate-week 02 --output-dir ~/Documents/week02/
```

### Generate all labs at once

```bash
gensec-template generate-all
```

### Other commands

```bash
# Show version
gensec-template --version

# Clear cached data
gensec-template clear-cache

# Show cache info
gensec-template cache-info
```

## Output Format

Generated `.docx` files are compatible with:
- **Google Docs** (upload to Drive and open)
- **Microsoft Word** (2016+)
- **LibreOffice Writer**

The template structure:
```
# 01.3: Programmatic Model Access    [Heading 1]

## 1. Models via APIs                [Heading 2]
• Take a screenshot of the results for one of the prompts
  that includes your OdinId
  [Screenshot Required]

[Answer:]


## 2. Ollama                         [Heading 2]
• Take a screenshot of the results...

[Answer:]
```

## Requirements

- Python 3.10 or higher
- Internet connection (to fetch lab content)

## Troubleshooting

### Command not found after install

Add the install location to your PATH:

```bash
# For pip install --user
export PATH="$HOME/.local/bin:$PATH"

# Add to your shell config (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Network errors

The tool requires internet access to fetch lab content. If you see connection errors:
1. Check your internet connection
2. Try again - the course website might be temporarily unavailable
3. Use `gensec-template clear-cache` if data seems stale

### Permission denied

On Linux/macOS, make the install script executable:
```bash
chmod +x install.sh
./install.sh
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check .
```

## License

MIT License - Feel free to use and modify for your coursework.

## Contributing

Found a bug or want to add a feature? Open an issue or PR!
