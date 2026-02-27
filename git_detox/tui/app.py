from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Label, Button
from textual.containers import Horizontal, Vertical, Container
from textual.screen import ModalScreen
from git_detox.core.scanner import Scanner
from git_detox.utils.git_runner import GitRunner

class RestoreDialog(ModalScreen):
    def __init__(self, item_id, commit_hash):
        super().__init__()
        self.item_id = item_id
        self.commit_hash = commit_hash

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Restore {self.item_id}?"),
            Label(f"This will create a new branch at {self.commit_hash[:10]}"),
            Horizontal(
                Button("Restore", variant="success", id="restore_btn"),
                Button("Cancel", variant="error", id="cancel_btn"),
            ),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "restore_btn":
            branch_name = f"recovered-{self.item_id}"
            try:
                GitRunner.run(["branch", branch_name, self.commit_hash])
                self.dismiss(True)
            except Exception:
                self.dismiss(False)
        else:
            self.dismiss(None)

class GitDetoxTUI(App):
    CSS = """
    DataTable {
        height: 1fr;
        border: solid green;
    }
    #preview {
        width: 40%;
        height: 1fr;
        border: solid blue;
        padding: 1;
        overflow-y: scroll;
    }
    #dialog {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
        align: center middle;
    }
    #dialog Label {
        margin-bottom: 1;
        text-align: center;
        width: 100%;
    }
    #dialog Horizontal {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    #dialog Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "restore", "Restore"),
        ("s", "scan", "Rescan"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield DataTable()
            yield Static(id="preview", content="Select an item to see details")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Type", "Ref", "Subject", "Risk", "Date")
        table.cursor_type = "row"
        self.action_scan()

    def action_scan(self) -> None:
        scanner = Scanner()
        self.items = scanner.scan_all()
        table = self.query_one(DataTable)
        table.clear()
        risk_colors = {"low": "green", "medium": "yellow", "high": "red"}
        for item in self.items:
            risk_text = f'''[{risk_colors.get(item.risk_level, 'white')}]{item.risk_level}[/]'''
            table.add_row(
                item.id,
                item.type,
                item.source_ref or "N/A",
                item.commit.subject,
                risk_text,
                item.commit.timestamp.strftime("%Y-%m-%d %H:%M"),
                key=item.id
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        item_id = event.row_key.value
        item = next((i for i in self.items if i.id == item_id), None)
        if item:
            diff = GitRunner.run(["show", "--stat", item.commit.hash])
            details = f'''[bold cyan]{item.id}[/bold cyan]\n'''
            details += f"Type: {item.type}\n"
            details += f"Commit: {item.commit.hash[:10]}\n"
            details += f"Subject: {item.commit.subject}\n"
            details += f"Risk: {item.risk_level}\n\n"
            details += f'''[yellow]Diff Summary:[/yellow]\n{diff}'''
            self.query_one("#preview").update(details)

    def action_restore(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            item_id = row_key.value
            item = next((i for i in self.items if i.id == item_id), None)
            if item:
                def check_restore(result):
                    if result is True:
                        self.notify(f"Restored to branch: recovered-{item_id}")
                        self.action_scan()
                    elif result is False:
                        self.notify("Restoration failed", severity="error")

                self.push_screen(RestoreDialog(item_id, item.commit.hash), check_restore)

if __name__ == "__main__":
    app = GitDetoxTUI()
    app.run()
