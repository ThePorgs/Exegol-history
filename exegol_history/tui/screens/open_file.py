from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Static, DirectoryTree, Button, Input
from textual.containers import Container
from exegol_history.tui.widgets.action_buttons import ActionButtons, ID_CONFIRM_BUTTON

ID_PATH_INPUT = "select_path_input"


class OpenFileScreen(ModalScreen):
    def __init__(self, message: str = ""):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        container = Container()
        container.border_title = "📁 Opening a file/folder"
        with container:
            yield Static(
                self.message,
                id="question",
            )
            yield DirectoryTree("/", id="directory_tree")
            yield Input(placeholder="Selected path...", id=ID_PATH_INPUT)
            yield ActionButtons()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self.screen.query_one(f"#{ID_PATH_INPUT}", Input).value = f"{event.path}"

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.screen.query_one(f"#{ID_PATH_INPUT}", Input).value = f"{event.path}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ID_CONFIRM_BUTTON:
            self.screen.dismiss(self.screen.query_one(f"#{ID_PATH_INPUT}", Input).value)
