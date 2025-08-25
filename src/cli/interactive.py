"""
Interactive CLI session manager with slash commands.
Handles user input, command parsing, and simple conversation history.
"""

from datetime import datetime
from typing import Any
from src.utils.config import Config

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class InteractiveSession:
    """
    Manages interactive CLI session with slash commands and natural language queries.
    """

    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.conversation_history: list[dict[str, Any]] = []
        self.running = True
        self.session_title = "BI Chat Session"
        self.created_at = datetime.now()

    def run(self) -> None:
        """Main interactive loop."""
        # Show session info
        self._show_session_info()

        while self.running:
            try:
                # Get user input with session-aware prompt
                prompt_text = f"[{self.session_title}] > "
                user_input = Prompt.ask(prompt_text).strip()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input.startswith("/"):
                    self._handle_slash_command(user_input)
                else:
                    # Handle natural language query
                    self._handle_query(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except EOFError:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")

    def _handle_slash_command(self, command: str) -> None:
        """Process slash commands."""
        # Parse command and arguments
        parts = command[1:].split(None, 1)  # Remove leading '/'
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "help":
            self._show_help()
        elif cmd == "clear":
            self._clear_history()
        elif cmd == "exit":
            self.running = False
        elif cmd in ["sessions", "new", "switch", "delete"]:
            self.console.print(
                "[red]❌ Multiple sessions not available in this version.[/red]"
            )
        else:
            self.console.print(
                f"[red]❌ Unknown command: /{cmd}[/red]\n"
                "Type [bold]/help[/bold] for available commands."
            )

    def _handle_query(self, query: str) -> None:
        """Process natural language queries."""
        try:
            # Add query to history
            self._add_message("user", query)

            self.console.print(f"[blue]🔍 Processing query:[/blue] {query}")

            # Generate placeholder response
            response = self._generate_placeholder_response(query)

            # Add response to history
            self._add_message("assistant", response)

            self.console.print(f"[green]🤖 Response:[/green] {response}")

        except Exception as e:
            self.console.print(f"[red]Query processing error: {e}[/red]")

    def _add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,  # 'user' or 'assistant'
            "content": content,
        }
        self.conversation_history.append(message)

    def _generate_placeholder_response(self, query: str) -> str:
        """Generate placeholder response until Agent 2 implements CrewAI system."""
        return (
            f"I understand you want to analyze: '{query}'. "
            "The CrewAI agent system is being implemented by Agent 2. "
            "This will soon generate SQL queries, analyze BigQuery data, "
            "and provide insights."
        )

    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
[bold cyan]📋 BI Chat CLI Commands (Single Session Mode)[/bold cyan]

[bold yellow]Current Session:[/bold yellow]
  [green]/clear[/green]                       - Clear conversation history

[bold yellow]System:[/bold yellow]
  [green]/help[/green]                        - Show this help
  [green]/exit[/green]                        - Exit CLI

[bold yellow]Natural Language Queries:[/bold yellow]
Just type your question naturally (no slash prefix):
  [dim]show me revenue trends for last week[/dim]
  [dim]what are the top user transactions[/dim]
  [dim]analyze user behavior patterns[/dim]

[bold yellow]Safety Features:[/bold yellow]
• Queries automatically limited to last 30 days
• Read-only access to BigQuery data
• Simple conversation history in memory

[bold red]Note:[/bold red] Multiple session support coming in next version.
        """.strip()

        panel = Panel(help_text, border_style="cyan", padding=(1, 2))
        self.console.print(panel)

    def _clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        self.console.print("[green]✅ Conversation history cleared[/green]")

    def _show_session_info(self) -> None:
        """Display current session information."""
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M')
        panel = Panel(
            f"[bold]{self.session_title}[/bold]\n"
            f"Created: {created_str}\n"
            f"Messages: {len(self.conversation_history)}",
            title="Current Session",
            border_style="green",
        )
        self.console.print(panel)