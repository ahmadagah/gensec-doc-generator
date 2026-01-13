"""
Command-line interface for the gensec-template CLI tool.

This module provides the CLI commands for listing labs, generating templates,
and managing the cache.
"""

import re
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .cache import get_cache, clear_global_cache
from .generator import generate_docx, generate_markdown
from .models import Lab, LabIndex
from .scraper import get_scraper, ScraperError

__version__ = "0.1.0"

# Create the CLI app
app = typer.Typer(
    name="gensec-template",
    help="Generate Google Docs templates for CS 475/575 Gen-Sec labs",
    add_completion=False,
    no_args_is_help=True,
)

# Console for rich output
console = Console()

# Default output directory
DEFAULT_OUTPUT_DIR = Path("./output")


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]gensec-template[/bold cyan] version {__version__}")
        console.print("[dim]Generate Google Docs templates for CS 475/575 Gen-Sec labs[/dim]")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    GenSec Lab Template Generator

    Generate Google Docs-compatible templates for CS 475/575
    Generative Security Application Engineering lab assignments.

    Run 'gensec-template list' to see available labs.
    """
    pass


def print_error(message: str, hint: str = None):
    """Print a formatted error message."""
    console.print(f"\n[red bold]Error:[/red bold] {message}")
    if hint:
        console.print(f"[dim]Hint: {hint}[/dim]")
    console.print()


def print_network_error():
    """Print a helpful network error message."""
    print_error(
        "Could not connect to the course website",
        "Check your internet connection and try again. "
        "The website might also be temporarily unavailable."
    )


def get_lab_index_with_cache() -> LabIndex:
    """Get the lab index, using cache if available."""
    cache = get_cache()
    index = cache.get_lab_index()

    if index is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Fetching lab index...", total=None)
            scraper = get_scraper()
            index = scraper.scrape_lab_index_sync()
            cache.set_lab_index(index)

    return index


def get_full_lab(lab_id_or_number: str, use_cache: bool = True) -> Optional[Lab]:
    """Get a full lab with sections, using cache if available."""
    cache = get_cache()

    # Try to find by ID first, then by number
    index = get_lab_index_with_cache()
    lab = index.get_lab_by_id(lab_id_or_number)
    if not lab:
        lab = index.get_lab_by_number(lab_id_or_number)

    if not lab:
        return None

    # Check cache for full lab
    if use_cache:
        cached_lab = cache.get_lab(lab.lab_id)
        if cached_lab and cached_lab.sections:
            return cached_lab

    # Scrape sections
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"Fetching sections for {lab.number}: {lab.title}...", total=None)
        scraper = get_scraper()
        lab = scraper.scrape_lab_sections_sync(lab)
        cache.set_lab(lab)

    return lab


def resolve_lab_identifier(identifier: str) -> Optional[str]:
    """
    Resolve a lab identifier (number, ID, or URL) to a lab number or ID.

    Args:
        identifier: Lab number (01.3), ID (G01.3_ProgramModel), or URL.

    Returns:
        The lab ID or number, or None if it can't be resolved.
    """
    # Check if it's a URL
    if identifier.startswith("http"):
        # Extract lab ID from URL
        match = re.search(r"/labs/([^/]+)/", identifier)
        if match:
            return match.group(1)
        return None

    return identifier


@app.command("list")
def list_labs():
    """List all available labs from the course website."""
    try:
        index = get_lab_index_with_cache()

        if not index.labs:
            console.print("[yellow]No labs found.[/yellow]")
            return

        # Create a nice table
        table = Table(title="CS 475/575: Generative Security Application Engineering")
        table.add_column("Number", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Duration", style="green", justify="right")

        for lab in index.get_labs_sorted():
            duration = f"{lab.duration_minutes} min" if lab.duration_minutes else "-"
            table.add_row(lab.number, lab.title, duration)

        console.print(table)
        console.print(f"\n[dim]Total: {index.lab_count} labs[/dim]")
        console.print("[dim]Run 'gensec-template generate <number>' to create a template[/dim]")

    except ScraperError:
        print_network_error()
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("generate")
def generate(
    identifier: str = typer.Argument(
        ...,
        help="Lab number (e.g., 01.3), ID (e.g., G01.3_ProgramModel), or URL",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. Defaults to ./output/<lab_number>_<title>.docx",
    ),
    format: str = typer.Option(
        "docx",
        "--format",
        "-f",
        help="Output format: docx or md",
    ),
):
    """Generate a template for a specific lab."""
    try:
        # Resolve the identifier
        lab_ref = resolve_lab_identifier(identifier)
        if not lab_ref:
            console.print(f"[red]Invalid lab identifier: {identifier}[/red]")
            raise typer.Exit(1)

        # Get the full lab
        lab = get_full_lab(lab_ref)
        if not lab:
            console.print(f"[red]Lab not found: {identifier}[/red]")
            console.print("[dim]Use 'gensec-template list' to see available labs[/dim]")
            raise typer.Exit(1)

        # Determine output path
        if output is None:
            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            safe_title = re.sub(r"[^\w\s-]", "", lab.title).replace(" ", "_")
            ext = "md" if format == "md" else "docx"
            output = DEFAULT_OUTPUT_DIR / f"{lab.number}_{safe_title}.{ext}"

        # Generate the template
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Generating template...", total=None)

            if format == "md":
                generate_markdown(lab, str(output))
            else:
                generate_docx(lab, str(output))

        # Show summary
        console.print(f"\n[green]Template generated successfully![/green]")
        console.print(f"[dim]Lab:[/dim] {lab.number}: {lab.title}")
        console.print(f"[dim]Sections:[/dim] {lab.section_count}")
        console.print(f"[dim]Questions:[/dim] {lab.total_questions}")
        console.print(f"\n[bold]Output:[/bold] {output}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("generate-week")
def generate_week(
    week: str = typer.Argument(
        ...,
        help="Week number (e.g., 01 for all 01.x labs)",
    ),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        "--output-dir",
        "-d",
        help="Output directory for generated files",
    ),
    format: str = typer.Option(
        "docx",
        "--format",
        "-f",
        help="Output format: docx or md",
    ),
):
    """Generate templates for all labs in a week."""
    try:
        index = get_lab_index_with_cache()

        # Find all labs for the week
        week_labs = [lab for lab in index.labs if lab.number.startswith(f"{week}.")]

        if not week_labs:
            console.print(f"[yellow]No labs found for week {week}[/yellow]")
            raise typer.Exit(1)

        console.print(f"[bold]Generating templates for week {week}...[/bold]\n")

        output_dir.mkdir(parents=True, exist_ok=True)

        for lab in sorted(week_labs, key=lambda x: x.number):
            console.print(f"  Processing {lab.number}: {lab.title}...")

            # Get full lab
            full_lab = get_full_lab(lab.lab_id)
            if not full_lab:
                console.print(f"    [yellow]Warning: Could not fetch lab[/yellow]")
                continue

            # Generate output
            safe_title = re.sub(r"[^\w\s-]", "", full_lab.title).replace(" ", "_")
            ext = "md" if format == "md" else "docx"
            output_path = output_dir / f"{full_lab.number}_{safe_title}.{ext}"

            if format == "md":
                generate_markdown(full_lab, str(output_path))
            else:
                generate_docx(full_lab, str(output_path))

            console.print(
                f"    [green]Created:[/green] {output_path.name} "
                f"({full_lab.section_count} sections, {full_lab.total_questions} questions)"
            )

        console.print(f"\n[green]All templates saved to: {output_dir}[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("generate-all")
def generate_all(
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        "--output-dir",
        "-d",
        help="Output directory for generated files",
    ),
    format: str = typer.Option(
        "docx",
        "--format",
        "-f",
        help="Output format: docx or md",
    ),
):
    """Generate templates for all available labs."""
    try:
        index = get_lab_index_with_cache()

        if not index.labs:
            console.print("[yellow]No labs found.[/yellow]")
            raise typer.Exit(1)

        console.print(f"[bold]Generating templates for all {index.lab_count} labs...[/bold]\n")

        output_dir.mkdir(parents=True, exist_ok=True)
        success_count = 0

        for lab in index.get_labs_sorted():
            console.print(f"  Processing {lab.number}: {lab.title}...")

            try:
                # Get full lab
                full_lab = get_full_lab(lab.lab_id)
                if not full_lab:
                    console.print(f"    [yellow]Warning: Could not fetch lab[/yellow]")
                    continue

                # Generate output
                safe_title = re.sub(r"[^\w\s-]", "", full_lab.title).replace(" ", "_")
                ext = "md" if format == "md" else "docx"
                output_path = output_dir / f"{full_lab.number}_{safe_title}.{ext}"

                if format == "md":
                    generate_markdown(full_lab, str(output_path))
                else:
                    generate_docx(full_lab, str(output_path))

                console.print(
                    f"    [green]Created:[/green] {output_path.name} "
                    f"({full_lab.section_count} sections, {full_lab.total_questions} questions)"
                )
                success_count += 1

            except Exception as e:
                console.print(f"    [red]Error: {e}[/red]")

        console.print(
            f"\n[green]Generated {success_count}/{index.lab_count} templates[/green]"
        )
        console.print(f"[dim]Output directory: {output_dir}[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("clear-cache")
def clear_cache():
    """Clear the cached lab data."""
    try:
        cache = get_cache()
        info = cache.get_cache_info()

        if info.entry_count == 0:
            console.print("[dim]Cache is already empty.[/dim]")
            return

        console.print(f"[dim]Cache location: {info.directory}[/dim]")
        console.print(f"[dim]Entries: {info.entry_count}[/dim]")

        clear_global_cache()
        console.print("[green]Cache cleared successfully.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("cache-info")
def cache_info():
    """Show cache information and statistics."""
    try:
        cache = get_cache()
        info = cache.get_cache_info()

        console.print("[bold]Cache Information[/bold]\n")
        console.print(f"  [dim]Directory:[/dim] {info.directory}")
        console.print(f"  [dim]Size:[/dim] {info.size_bytes / 1024:.1f} KB")
        console.print(f"  [dim]Entries:[/dim] {info.entry_count}")

        if info.lab_index_cached:
            age = info.lab_index_age or "unknown"
            console.print(f"  [dim]Lab index:[/dim] cached ({age})")
        else:
            console.print(f"  [dim]Lab index:[/dim] not cached")

        if info.cached_labs:
            console.print(f"\n  [dim]Cached labs ({len(info.cached_labs)}):[/dim]")
            for lab_id in sorted(info.cached_labs):
                console.print(f"    - {lab_id}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
