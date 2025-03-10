from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, DirectoryTree, Button, Label
from textual.containers import Horizontal, Vertical


class OpenFileScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield DirectoryTree("/", id="file_tree")
            with Horizontal():
                yield Label("Selected file:")
                yield Static("", id="label_selected_path")
            with Horizontal(id="add_confirm"):
                yield Button(" Confirm", variant="success", id="select_button")
                yield Button(" Cancel", variant="error", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_button":
            self.app.pop_screen()
        else:
            self.dismiss(self.query_one("#label_selected_path", Static)._content)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self.query_one("#label_selected_path", Static).update(f"{event.path}")
