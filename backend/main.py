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

VERSION = "v3.0"

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
    # Startup Animation
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
    # Banner
    # --------------------------
    fig = Figlet(font="slant")
    ascii_banner = fig.renderText("SAFE SQL")

    gradient_colors = ["cyan", "bright_cyan", "blue", "bright_blue"]
    banner_text = Text()

    for i, line in enumerate(ascii_banner.splitlines()):
        color = gradient_colors[i % len(gradient_colors)]
        banner_text.append(line + "\n", style=f"bold {color}")

    console.print(Align.center(banner_text))
    console.print(Align.center(Text(f"SAFE SQL {VERSION}", style="bold green")))
    console.print()

    # --------------------------
    # USER LOGIN
    # --------------------------
    username = console.input("[bold cyan]Enter username:[/bold cyan] ").strip()

    if not username:
        console.print("[red]Username required.[/red]")
        exit()

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

    db_interface = DatabaseInterface(db_config)
    dp_instance = privacy.DifferentialPrivacy(epsilon=1.0)
    dp_instance.register_user(username, total_budget=10.0)

    eco_scheduler_instance = EcoScheduler(query_buffer_size=5)

    total_queries = 0
    total_emissions = 0.0
    total_execution_time = 0.0

    diagnostics = Table(show_header=False, box=None)
    diagnostics.add_column("Component", style="bold")
    diagnostics.add_column("Status")

    diagnostics.add_row("Database Connection", "[green]✓ Connected[/green]")
    diagnostics.add_row("Differential Privacy", "[green]✓ Ready[/green]")
    diagnostics.add_row("Energy Tracker", "[green]✓ Ready[/green]")

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

    # --------------------------
    # CLI LOOP
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

        # --------------------------
        # Runtime Commands
        # --------------------------
        if user_query.startswith("\\epsilon"):
            try:
                value = float(user_query.split()[1])
                dp_instance.set_epsilon(value)
                console.print(f"[green]Epsilon updated to {value}[/green]")
            except:
                console.print("[red]Usage: \\epsilon <value>[/red]")
            continue

        if user_query.startswith("\\mode"):
            try:
                mode = user_query.split()[1]
                dp_instance.set_mode(mode)
                console.print(f"[green]Mode switched to {mode}[/green]")
            except:
                console.print("[red]Usage: \\mode raw|private|audit[/red]")
            continue

        if user_query.startswith("\\metrics"):

            metrics = dp_instance.get_metrics(username)

            metrics_table = Table(show_header=False)
            metrics_table.add_row("User", username)
            metrics_table.add_row("Total Queries", str(total_queries))
            metrics_table.add_row("Total Emissions (kg CO2)", f"{total_emissions:.6f}")
            metrics_table.add_row(
                "Avg Execution Time (sec)",
                f"{(total_execution_time/total_queries):.4f}" if total_queries else "0"
            )
            metrics_table.add_row("Epsilon", str(metrics["epsilon"]))
            metrics_table.add_row("Remaining Budget", str(metrics["remaining_budget"]))
            metrics_table.add_row("Mode", metrics["mode"])

            console.print(Panel(metrics_table, title="Live Metrics Dashboard", border_style="cyan"))
            continue

        # --------------------------
        # Execute SQL
        # --------------------------
        try:
            with console.status("[bold green]Executing query...[/bold green]", spinner="dots"):

                start_time = time.time()
                eco_scheduler_instance.start_tracking()

                result, columns = db_interface.execute_query(user_query)
                privacy_output = dp_instance.process_result(username, user_query, result)

                emissions = eco_scheduler_instance.stop_tracking()
                end_time = time.time()

                execution_time = end_time - start_time

            total_queries += 1
            total_emissions += emissions
            total_execution_time += execution_time

            if privacy_output is None:
                console.print("[green]Query executed successfully.[/green]")
                continue

            raw = privacy_output["raw"]
            private = privacy_output["private"]
            noise = privacy_output["noise"]

            if private:
                table = Table(show_header=True, header_style="bold magenta")
                for col in columns:
                    table.add_column(col)
                for row in private:
                    table.add_row(*[str(item) for item in row])
                console.print(table)

            if dp_instance.mode == "audit" and raw is not None:
                console.print(Panel(f"Raw Result:\n{raw}", border_style="yellow"))
                console.print(Panel(f"Noise Added:\n{noise}", border_style="red"))

            console.print(
                Panel.fit(
                    f"[bold cyan]Execution Time:[/bold cyan] {execution_time:.4f} sec\n"
                    f"[bold green]Epsilon:[/bold green] {dp_instance.epsilon}\n"
                    f"[bold yellow]Remaining Budget:[/bold yellow] "
                    f"{dp_instance.get_remaining_budget(username)}\n"
                    f"[bold magenta]Emissions:[/bold magenta] {emissions:.6f} kg CO2",
                    border_style="blue"
                )
            )

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")