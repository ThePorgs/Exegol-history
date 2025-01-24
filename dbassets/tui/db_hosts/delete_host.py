from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical, Container

"""
This screen is used to delete the selected host
"""


class DeleteHostConfirmationScreen(Screen):
    CSS_PATH = "../css/delete_object.tcss"

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Container(
                Label("Are you sure you want to remove that host?", id="question"),
                id="question-container",
            )
            with Horizontal(id="delete_confirm"):
                yield Button("Confirm", variant="success", id="confirm")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
