from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Horizontal

ID_CONFIRM_BUTTON = "confirm_button"
ID_CANCEL_BUTTON = "cancel_button"
ID_ACTIONS_HORIZONTAL = "actions_horizontal"


class ActionButtons(Static):
    def __init__(
        self,
        confirm_button_id: str = ID_CONFIRM_BUTTON,
        cancel_button_id: str = ID_CANCEL_BUTTON,
    ):
        super().__init__()
        self.confirm_button_id = confirm_button_id
        self.cancel_button_id = cancel_button_id

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button.success("Confirm", id=self.confirm_button_id),
            Button.error("Cancel", id=self.cancel_button_id),
            id=ID_ACTIONS_HORIZONTAL,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in ID_CANCEL_BUTTON:
            self.app.pop_screen()
