"""
AgentScope Local CLI
Command-line interface for managing the AgentScope Local flight recorder.
"""
import typer
import uvicorn
import sqlite3
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="agentscope-local",
    help="Universal AI debugging flight recorder",
    add_completion=False,
)
console = Console()

# Default paths
DEFAULT_DB = "debug_flight_recorder.db"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


@app.command()
def serve(
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(DEFAULT_PORT, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development"),
    db: str = typer.Option(DEFAULT_DB, "--db", "-d", help="Path to SQLite database"),
):
    """
    Start the AgentScope Local server.
    
    This will start both the API server and serve the web UI.
    Open http://localhost:8000 in your browser to view traces.
    """
    # Set environment variable for database path
    os.environ["AGENTSCOPE_DB_PATH"] = db
    
    console.print(Panel.fit(
        f"[bold cyan]AgentScope Local[/bold cyan]\n"
        f"[dim]Universal AI Debugging Flight Recorder[/dim]\n\n"
        f"🚀 Server: [green]http://{host}:{port}[/green]\n"
        f"💾 Database: [yellow]{db}[/yellow]\n"
        f"{'🔄 Auto-reload: [green]enabled[/green]' if reload else ''}",
        title="Starting Server",
        border_style="cyan"
    ))
    
    # Check if database exists
    if not Path(db).exists():
        console.print(f"[yellow]⚠ Database not found at {db}[/yellow]")
        console.print("[dim]The database will be created when traces are recorded.[/dim]\n")
    
    # Start server
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@app.command()
def clear(
    db: str = typer.Option(DEFAULT_DB, "--db", "-d", help="Path to SQLite database"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """
    Clear all traces from the database.
    
    This will delete all recorded traces, spans, and vectors.
    Use with caution!
    """
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[yellow]Database not found at {db}[/yellow]")
        return
    
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to clear all data from {db}?",
            default=False
        )
        if not confirm:
            console.print("[dim]Operation cancelled.[/dim]")
            return
    
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Get table counts before clearing
        stats = {}
        for table in ['spans', 'vector_metadata']:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0
        
        # Clear tables
        cursor.execute("DELETE FROM spans")
        cursor.execute("DELETE FROM vector_metadata")
        
        # Clear vector tables (they're virtual tables, so just recreate)
        # Get all vector tables
        vector_tables = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'vectors_%'
        """).fetchall()
        
        for (table_name,) in vector_tables:
            try:
                cursor.execute(f"DROP TABLE {table_name}")
            except:
                pass
        
        conn.commit()
        conn.close()
        
        # Show results
        table = Table(title="Database Cleared", show_header=True, header_style="bold cyan")
        table.add_column("Table", style="cyan")
        table.add_column("Rows Deleted", justify="right", style="yellow")
        
        for table_name, count in stats.items():
            table.add_row(table_name, str(count))
        
        console.print(table)
        console.print(f"\n[green]✓[/green] Database cleared: {db}")
        
    except Exception as e:
        console.print(f"[red]✗ Error clearing database:[/red] {e}")


@app.command()
def info(
    db: str = typer.Option(DEFAULT_DB, "--db", "-d", help="Path to SQLite database"),
):
    """
    Show database statistics and information.
    """
    db_path = Path(db)
    
    if not db_path.exists():
        console.print(f"[yellow]Database not found at {db}[/yellow]")
        console.print("[dim]Run some traced code to create the database.[/dim]")
        return
    
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Get counts
        span_count = cursor.execute("SELECT COUNT(*) FROM spans").fetchone()[0]
        trace_count = cursor.execute("SELECT COUNT(DISTINCT trace_id) FROM spans").fetchone()[0]
        vector_count = cursor.execute("SELECT COUNT(*) FROM vector_metadata").fetchone()[0]
        
        # Get LLM providers
        providers = cursor.execute("""
            SELECT DISTINCT provider, COUNT(*) as count
            FROM spans
            WHERE provider IS NOT NULL
            GROUP BY provider
            ORDER BY count DESC
        """).fetchall()
        
        # Get vector tables
        vector_tables = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'vectors_%'
            ORDER BY name
        """).fetchall()
        
        conn.close()
        
        # Display info
        console.print(Panel.fit(
            f"[bold cyan]Database: {db}[/bold cyan]\n"
            f"[dim]Size: {db_path.stat().st_size / 1024:.1f} KB[/dim]\n\n"
            f"📊 [bold]Statistics[/bold]\n"
            f"  Traces: [cyan]{trace_count}[/cyan]\n"
            f"  Spans: [cyan]{span_count}[/cyan]\n"
            f"  Vectors: [cyan]{vector_count}[/cyan]",
            border_style="cyan"
        ))
        
        if providers:
            provider_table = Table(title="LLM Providers", show_header=True, header_style="bold cyan")
            provider_table.add_column("Provider", style="cyan")
            provider_table.add_column("Calls", justify="right", style="yellow")
            
            for provider, count in providers:
                provider_table.add_row(provider or "unknown", str(count))
            
            console.print(provider_table)
        
        if vector_tables:
            console.print(f"\n[bold cyan]Vector Tables:[/bold cyan]")
            for (table_name,) in vector_tables:
                dimension = table_name.replace("vectors_", "")
                count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0] if db_path.exists() else 0
                console.print(f"  • {table_name} [dim](dimension: {dimension}, count: {count})[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗ Error reading database:[/red] {e}")


@app.callback()
def main():
    """
    AgentScope Local - Universal AI Debugging Flight Recorder
    
    Record, analyze, and debug LLM traces with RAG support.
    """
    pass


if __name__ == "__main__":
    app()
