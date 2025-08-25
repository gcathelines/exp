"""
Interactive CLI session manager with slash commands.
Handles user input, command parsing, and multi-session management.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.sessions.manager import SessionManager
from src.utils.config import Config
from src.utils.models import UserSession


class InteractiveSession:
    """
    Manages interactive CLI with multi-session support and slash commands.
    """

    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.session_manager = SessionManager()
        self.current_session: UserSession
        self.running = True
        self._initialize_session()

    def run(self) -> None:
        """Main interactive loop."""
        # Initialize or load existing session

        while self.running:
            try:
                prompt_text = f"[{self.current_session.title}] > "
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
                self.console.print("\n[yellow]👋 Session saved. Goodbye![/yellow]")
                break
            except EOFError:
                self.console.print("\n[yellow]👋 Session saved. Goodbye![/yellow]")
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
        elif cmd == "sessions":
            self._list_sessions()
        elif cmd == "new":
            self._create_new_session(args)
        elif cmd == "switch":
            self._switch_session(args)
        elif cmd == "delete":
            self._delete_session(args)
        elif cmd == "clear":
            self._clear_history()
        elif cmd == "exit":
            self.running = False
        else:
            self.console.print(
                f"[red]❌ Unknown command: /{cmd}[/red]\n"
                "Type [bold]/help[/bold] for available commands."
            )

    def _handle_query(self, query: str) -> None:
        """Process natural language queries."""
        try:
            # Add query to current session
            self.session_manager.add_message_to_session(
                self.current_session, "user", query
            )

            self.console.print(f"[blue]🔍 Processing query:[/blue] {query}")

            # Generate placeholder response
            response = self._generate_placeholder_response(query)

            # Add response to current session
            self.session_manager.add_message_to_session(
                self.current_session, "assistant", response
            )

            self.console.print(f"[green]🤖 Response:[/green] {response}")

        except Exception as e:
            self.console.print(f"[red]Query processing error: {e}[/red]")

    def _initialize_session(self) -> None:
        """Initialize session - create default or load most recent."""
        existing_sessions = self.session_manager.get_all_sessions()

        if existing_sessions:
            # Load the most recent session
            self.current_session = existing_sessions[0]
            self.console.print(
                f"[dim]Loaded recent session:[/dim] {self.current_session.title}"
            )
        else:
            # Create default session
            self.current_session = self.session_manager.create_session(
                "Default Session"
            )
            self.console.print("[dim]Created new default session[/dim]")

        self._show_session_info()

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
[bold cyan]📋 BI Chat CLI Commands (Multi-Session Mode)[/bold cyan]

[bold yellow]Session Management:[/bold yellow]
  [green]/sessions[/green]                     - List all sessions
  [green]/new "Session Name"[/green]          - Create new named session
  [green]/switch session-id[/green]          - Switch to existing session
  [green]/delete session-id[/green]           - Delete session by ID
  [green]/clear[/green]                       - Clear current session history

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
• Sessions persisted across CLI restarts

[bold green]✅ Multi-session support enabled![/bold green]
        """.strip()

        panel = Panel(help_text, border_style="cyan", padding=(1, 2))
        self.console.print(panel)

    def _list_sessions(self) -> None:
        """List all available sessions."""
        sessions = self.session_manager.get_all_sessions()

        if not sessions:
            self.console.print(
                '[yellow]📭 No sessions found. Use [bold]/new "Session Name"[/bold] '
                "to create one.[/yellow]"
            )
            return

        table = Table(title="📂 Available Sessions")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="bold")
        table.add_column("Created", style="green")
        table.add_column("Messages", justify="right", style="cyan")
        table.add_column("Active", justify="center")

        for session in sessions:
            is_current = "🟢" if session.id == self.current_session.id else ""
            table.add_row(
                str(session.id),
                session.title,
                session.created_at.strftime("%Y-%m-%d %H:%M"),
                str(session.get_message_count()),
                is_current,
            )

        self.console.print(table)

    def _create_new_session(self, args: str) -> None:
        """Create a new session."""
        if not args.strip():
            self.console.print(
                "[red]❌ Please provide a session name: "
                '[bold]/new "Session Name"[/bold][/red]'
            )
            return

        # Remove quotes if present
        session_name = args.strip().strip("\"'")

        try:
            new_session = self.session_manager.create_session(session_name)
            self.current_session = new_session
            self.console.print(
                f"[green]✅ Created and switched to new session:[/green] "
                f"[bold]{session_name}[/bold]"
            )
            self._show_session_info()
        except Exception as e:
            self.console.print(f"[red]❌ Failed to create session: {e}[/red]")

    def _switch_session(self, args: str) -> None:
        """Switch to a different session by ID."""
        if not args.strip():
            self.console.print(
                "[yellow]💡 Usage: [bold]/switch session-id[/bold][/yellow]"
            )
            self._list_sessions()
            return

        # Parse session ID
        try:
            session_id = int(args.strip())
        except ValueError:
            self.console.print(f"[red]❌ Invalid session ID:[/red] {args.strip()}")
            self.console.print(
                "[yellow]💡 Session ID must be a number. "
                "Use [bold]/sessions[/bold] to see available IDs.[/yellow]"
            )
            return

        session = self.session_manager.get_session_by_id(session_id)

        if not session:
            self.console.print(f"[red]❌ Session not found:[/red] {session_id}")
            return

        if session.id == self.current_session.id:
            self.console.print("[yellow]⚠️  Already in that session[/yellow]")
            return

        self.current_session = session
        self.console.print(
            f"[green]🔄 Switched to session:[/green] [bold]{session.title}[/bold]"
        )
        self._show_session_info()

    def _delete_session(self, args: str) -> None:
        """Delete a session by ID."""
        if not args.strip():
            self.console.print(
                "[red]❌ Please provide session ID: "
                "[bold]/delete session-id[/bold][/red]"
            )
            return

        session_identifier = args.strip()

        # Check if trying to delete current session
        try:
            session_id = int(session_identifier)
            if session_id == self.current_session.id:
                self.console.print(
                    "[red]❌ Cannot delete the current active session. "
                    "Switch to another session first.[/red]"
                )
                return
        except ValueError:
            pass

        # Parse and find the session to delete
        try:
            session_id = int(session_identifier)
        except ValueError:
            self.console.print(
                f"[red]❌ Invalid session ID:[/red] {session_identifier}"
            )
            return

        session_to_delete = self.session_manager.get_session_by_id(session_id)
        if not session_to_delete:
            self.console.print(f"[red]❌ Session not found:[/red] {session_id}")
            return

        # Check if it's the current session
        if session_to_delete.id == self.current_session.id:
            self.console.print(
                "[red]❌ Cannot delete the current active session. "
                "Switch to another session first.[/red]"
            )
            return

        try:
            if session_to_delete.id is None:
                self.console.print("[red]❌ Session has no valid ID[/red]")
                return

            success = self.session_manager.delete_session(session_to_delete.id)
            if success:
                self.console.print(
                    f"[green]✅ Deleted session:[/green] {session_to_delete.title}"
                )
            else:
                self.console.print("[red]❌ Failed to delete session[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to delete session: {e}[/red]")

    def _clear_history(self) -> None:
        """Clear current session's conversation history."""
        try:
            self.current_session.clear_history()
            self.session_manager.update_session_activity(self.current_session)
            self.console.print("[green]✅ Session history cleared[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to clear session: {e}[/red]")

    def _show_session_info(self) -> None:
        """Display current session information."""
        if self.current_session:
            created_str = self.current_session.created_at.strftime("%Y-%m-%d %H:%M")
            panel = Panel(
                f"[bold]{self.current_session.title}[/bold]\n"
                f"ID: {self.current_session.id}\n"
                f"Created: {created_str}\n"
                f"Messages: {self.current_session.get_message_count()}",
                title="Current Session",
                border_style="green",
            )
            self.console.print(panel)
