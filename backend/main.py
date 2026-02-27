from backend import privacy
from backend.db import DatabaseInterface
from backend.eco_scheduler import EcoScheduler

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import traceback
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

from pyfiglet import Figlet

import time
import os

traceback.install()
console = Console()

VERSION = "v1.0"

SQL_KEYWORDS = [
    "SELECT", "INSERT", "UPDATE", "DELETE",
    "FROM", "WHERE", "LIMIT", "VALUES",
    "CREATE", "DROP", "TABLE", "ALTER",
    "COUNT", "AVG", "SUM", "MIN", "MAX",
    "JOIN", "INNER", "LEFT", "RIGHT",
    "GROUP BY", "ORDER BY"
]

if __name__ == "__main__":

    # --------------------------
    # Animated Startup Intro
    # --------------------------
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Initializing SAFE SQL Engine...[/bold cyan]"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task("init", total=None)
        time.sleep(1.5)

    # --------------------------
    # Gradient ASCII Banner
    # --------------------------
    fig = Figlet(font="slant")
    ascii_banner = fig.renderText("SAFE SQL")

    gradient_colors = ["cyan", "bright_cyan", "blue", "bright_blue"]
    banner_text = Text()

    for i, line in enumerate(ascii_banner.splitlines()):
        color = gradient_colors[i % len(gradient_colors)]
        banner_text.append(line + "\n", style=f"bold {color}")

    console.print(Align.center(banner_text))
    console.print(
        Align.center(
            Text(f"SAFE SQL {VERSION}", style="bold green")
        )
    )

    console.print()

    # --------------------------
    # System Initialization
    # --------------------------
    db_config = {
        "host": "localhost",
        "database": "safe_sql_db",
        "user": "postgres",
        "password": "SQL",
        "port": "5432"
    }

    diagnostics = Table(show_header=False, box=None)
    diagnostics.add_column("Component", style="bold")
    diagnostics.add_column("Status")

    # DB Check
    try:
        db_interface = DatabaseInterface(db_config)
        diagnostics.add_row("Database Connection", "[green]✓ Connected[/green]")
    except Exception:
        diagnostics.add_row("Database Connection", "[red]✗ Failed[/red]")
        console.print(Panel(diagnostics, title="Startup Diagnostics", border_style="red"))
        exit()

    # Privacy Check
    try:
        dp_instance = privacy.DifferentialPrivacy(epsilon=1.0)
        diagnostics.add_row("Differential Privacy", "[green]✓ Ready[/green]")
    except Exception:
        diagnostics.add_row("Differential Privacy", "[red]✗ Failed[/red]")

    # Tracker Check
    try:
        eco_scheduler_instance = EcoScheduler(query_buffer_size=5)
        diagnostics.add_row("Energy Tracker", "[green]✓ Ready[/green]")
    except Exception:
        diagnostics.add_row("Energy Tracker", "[red]✗ Failed[/red]")

    console.print(Panel(diagnostics, title="Startup Diagnostics", border_style="green"))

    # --------------------------
    # Autocomplete Setup
    # --------------------------
    try:
        tables_result, _ = db_interface.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        )
        table_names = [row[0] for row in tables_result] if tables_result else []
    except:
        table_names = []

    completer = WordCompleter(SQL_KEYWORDS + table_names, ignore_case=True)

    history_file = os.path.join(os.path.dirname(__file__), ".safe_sql_history")
    session = PromptSession(history=FileHistory(history_file))

    console.print()

    # --------------------------
    # Main CLI Loop
    # --------------------------
    while True:

        try:
            user_query = session.prompt("\nSQL > ", completer=completer)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if user_query.lower() == "exit":
            console.print("[bold red]Shutting down SAFE SQL...[/bold red]")
            break

        try:
            with console.status("[bold green]Executing query...[/bold green]", spinner="dots"):

                start_time = time.time()
                eco_scheduler_instance.start_tracking()

                result, columns = db_interface.execute_query(user_query)
                private_result = dp_instance.privatize_result(result)

                emissions = eco_scheduler_instance.stop_tracking()
                end_time = time.time()

                execution_time = end_time - start_time

            if private_result:
                table = Table(show_header=True, header_style="bold magenta")

                for col in columns:
                    table.add_column(col)

                for row in private_result:
                    table.add_row(*[str(item) for item in row])

                console.print(table)

                console.print(
                    Panel.fit(
                        f"[bold cyan]Execution Time:[/bold cyan] {execution_time:.4f} sec\n"
                        f"[bold green]Epsilon:[/bold green] {dp_instance.epsilon}\n"
                        f"[bold yellow]Emissions:[/bold yellow] {emissions:.6f} kg CO2",
                        border_style="blue"
                    )
                )
            else:
                console.print(
                    Panel.fit(
                        f"[green]Query executed successfully.[/green]\n"
                        f"[bold cyan]Execution Time:[/bold cyan] {execution_time:.4f} sec\n"
                        f"[bold yellow]Emissions:[/bold yellow] {emissions:.6f} kg CO2",
                        border_style="blue"
                    )
                )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")