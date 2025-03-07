from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Button, Input
from textual.containers import Vertical, Horizontal

"""
This screen is used to edit hosts informations such as the username, password, ...
"""


class EditHostScreen(ModalScreen):
    CSS_PATH = "../css/edit_object.tcss"

    def __init__(self, ip: str, hostname: str, role: str):
        super().__init__()
        self.ip = ip
        self.hostname = hostname
        self.role = role

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="IP", id="ip", value=self.ip)
            yield Input(placeholder="Hostname", id="hostname", value=self.hostname)
            yield Input(placeholder="Role", id="role", value=self.role)

            with Horizontal(id="edit_confirm"):
                yield Button("Confirm", variant="success", id="confirm")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            old_ip = self.ip
            ip = self.query_one("#ip", Input).value
            hostname = self.query_one("#hostname", Input).value
            role = self.query_one("#role", Input).value

            if ip:
                self.dismiss((old_ip, ip, hostname, role))
        else:
            self.app.pop_screen()
