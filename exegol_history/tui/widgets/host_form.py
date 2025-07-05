from textual.app import ComposeResult
from textual.widgets import (
    Button,
    Input,
)
from textual.containers import Container
from exegol_history.db_api.hosts import Host
from exegol_history.tui.widgets.action_buttons import ActionButtons

ID_IP_INPUT = "ip_input"
ID_HOSTNAME_INPUT = "hostname_input"
ID_ROLE_INPUT = "role_input"

ID_ACTIONS_HORIZONTAL = "actions_horizontal"

ID_CONFIRM_BUTTON = "confirm_button"
ID_CANCEL_BUTTON = "cancel_button"


class HostForm(Container):
    def __init__(self, host: Host = None, id: str = None):
        super().__init__(id=id)
        self.host = host
        self.button_clicked = None

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="IP",
            id=ID_IP_INPUT,
            value=self.host.ip if self.host else "",
        )
        yield Input(
            placeholder="Hostname",
            id=ID_HOSTNAME_INPUT,
            value=self.host.hostname if self.host else "",
        )
        yield Input(
            placeholder="Role",
            id=ID_ROLE_INPUT,
            value=self.host.role if self.host else "",
        )
        yield ActionButtons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ID_CONFIRM_BUTTON:
            self.host = Host(
                self.host.id if self.host else "",
                self.screen.query_one(f"#{ID_IP_INPUT}", Input).value,
                self.screen.query_one(f"#{ID_HOSTNAME_INPUT}", Input).value,
                self.screen.query_one(f"#{ID_ROLE_INPUT}", Input).value,
            )

            self.screen.dismiss([self.host])
