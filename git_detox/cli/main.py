import click
from rich.console import Console
from git_detox.utils.git_runner import GitRunner

console = Console()

@click.group()
def main():
    """Git Detox: Your Git Safety Net and Hygiene Tool."""
    if not GitRunner.is_repo():
        console.print("[red]Error: Not a git repository (or any of the parent directories)[/red]")
        exit(1)

from git_detox.core.scanner import Scanner
from rich.table import Table

@main.command()
def tui():
    """Launch the visual TUI interface."""
    from git_detox.tui.app import GitDetoxTUI
    app = GitDetoxTUI()
    app.run()

from git_detox.core.hygiene import HygieneAnalyzer

@main.command()
def health():
    """Analyse repository health and hygiene."""
    console.print("[yellow]Analyzing repository health...[/yellow]")
    analyzer = HygieneAnalyzer()
    health = analyzer.get_health_score()
    
    score = health['score']
    color = "green" if score > 80 else "yellow" if score > 50 else "red"
    
    console.print(f"\n[bold]Health Score: [{color}]{score}/100[/{color}][/bold]")
    console.print(f"Merged branches: {health['merged_count']}")
    console.print(f"Stale branches: {health['stale_count']}")
    
    if any(health['recommendations']):
        console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        for rec in health['recommendations']:
            if rec:
                console.print(f" • {rec}")

@main.command()
def scan():
    """Scan for recoverable work and hygiene issues."""
    console.print("[yellow]Scanning repository...[/yellow]")
    scanner = Scanner()
    items = scanner.scan_all()
    
    if not items:
        console.print("[green]No recoverable items found. Your repo is clean![/green]")
        return

    table = Table(title="Recoverable Git Work")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Source/Ref", style="green")
    table.add_column("Subject", style="white")
    table.add_column("Risk", style="bold")
    table.add_column("Date", style="blue")

    risk_colors = {"low": "green", "medium": "yellow", "high": "red"}

    for item in items:
        table.add_row(
            item.id,
            item.type,
            item.source_ref or "N/A",
            item.commit.subject,
            f"[{risk_colors.get(item.risk_level, 'white')}]{item.risk_level}[/]",
            item.commit.timestamp.strftime("%Y-%m-%d %H:%M")
        )
    
    console.print(table)
    console.print("\nUse [bold]git-detox show <ID>[/bold] to see details or [bold]git-detox restore <ID>[/bold] to recover.")

@main.command()
@click.argument('item_id')
def show(item_id):
    """Show details of a specific recoverable item."""
    scanner = Scanner()
    items = scanner.scan_all()
    item = next((i for i in items if i.id == item_id), None)
    
    if not item:
        console.print(f"[red]Error: Item {item_id} not found.[/red]")
        return

    console.print(f"[bold cyan]Details for {item_id}[/bold cyan]")
    console.print(f"Type: {item.type}")
    console.print(f"Commit: {item.commit.hash}")
    console.print(f"Author: {item.commit.author} <{item.commit.email}>")
    console.print(f"Date: {item.commit.timestamp}")
    console.print(f"Subject: [bold]{item.commit.subject}[/bold]")
    if item.commit.body:
        console.print(f"\n{item.commit.body}")
    
    console.print("\n[yellow]Diff Summary:[/yellow]")
    diff = GitRunner.run(["show", "--stat", item.commit.hash])
    console.print(diff)

@main.command()
@click.argument('item_id')
@click.option('--name', help='New branch name for restoration')
def restore(item_id, name):
    """Restore a specific item by creating a new branch."""
    scanner = Scanner()
    items = scanner.scan_all()
    item = next((i for i in items if i.id == item_id), None)
    
    if not item:
        console.print(f"[red]Error: Item {item_id} not found.[/red]")
        return

    branch_name = name or f"recovered-{item_id}"
    
    console.print(f"[yellow]Restoration Plan:[/yellow]")
    console.print(f"Command: [bold]git branch {branch_name} {item.commit.hash}[/bold]")
    
    if click.confirm("Do you want to proceed?"):
        try:
            GitRunner.run(["branch", branch_name, item.commit.hash])
            console.print(f"[green]Successfully restored to branch: {branch_name}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to restore: {str(e)}[/red]")

if __name__ == "__main__":
    main()
