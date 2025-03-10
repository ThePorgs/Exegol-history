from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Button, Input
from textual.containers import Vertical, Horizontal

"""
This screen is used to edit credentials informations such as the username, password, ...
"""


class EditCredentialScreen(ModalScreen):
    CSS_PATH = "../css/edit_object.tcss"

    def __init__(self, username: str, password: str, hash: str, domain: str):
        super().__init__()
        self.username = username
        self.password = password
        self.hash = hash
        self.domain = domain

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Username", id="username", value=self.username)
            yield Input(placeholder="Password", id="password", value=self.password)
            yield Input(placeholder="Hash", id="hash", value=self.hash)
            yield Input(placeholder="Domain", id="domain", value=self.domain)
            with Horizontal(id="edit_confirm"):
                yield Button("Confirm", variant="success", id="confirm")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            old_username = self.username
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            hash = self.query_one("#hash", Input).value
            domain = self.query_one("#domain", Input).value

            if username:
                self.dismiss((old_username, username, password, hash, domain))
        else:
            self.app.pop_screen()
