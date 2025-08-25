"""
BI Chat CLI - Interactive Business Intelligence CLI
Entry point for the application.
"""

import sys

import click
from rich.console import Console

from src.cli.interactive import InteractiveSession
from src.utils.config import load_config

console = Console()


@click.command()
def main() -> None:
    """BI Chat CLI - Analyze BigQuery data using natural language."""
    try:
        # Load configuration
        app_config = load_config()

        # Start interactive mode
        console.print("[bold green]🤖 BI Chat CLI - Interactive Mode[/bold green]")
        console.print(
            "Type [bold]/help[/bold] for available commands or ask questions "
            "about your data."
        )
        console.print("Press [bold]Ctrl+C[/bold] to exit.\n")

        session_manager = InteractiveSession(config=app_config)
        session_manager.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
