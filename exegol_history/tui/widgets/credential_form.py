from textual.app import ComposeResult
from textual.widgets import Button, Input
from textual.containers import (
    Container,
)
from exegol_history.db_api.creds import Credential
from exegol_history.tui.widgets.action_buttons import ActionButtons

ID_USERNAME_INPUT = "username_input"
ID_PASSWORD_INPUT = "password_input"
ID_HASH_INPUT = "hash_input"
ID_DOMAIN_INPUT = "domain_input"

ID_ACTIONS_HORIZONTAL = "actions_horizontal"
ID_LIMITED_HORIZONTAL = "limited_horizontal"

ID_CONFIRM_BUTTON = "confirm_button"
ID_CANCEL_BUTTON = "cancel_button"


class CredentialForm(Container):
    def __init__(self, credential: Credential = None, id: str = None):
        super().__init__(id=id)
        self.credential = credential
        self.button_clicked = None

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Username",
            id=ID_USERNAME_INPUT,
            value=self.credential.username if self.credential else "",
        )
        yield Input(
            placeholder="Password",
            id=ID_PASSWORD_INPUT,
            value=self.credential.password if self.credential else "",
        )
        yield Input(
            placeholder="Hash",
            id=ID_HASH_INPUT,
            value=self.credential.hash if self.credential else "",
        )
        yield Input(
            placeholder="Domain",
            id=ID_DOMAIN_INPUT,
            value=self.credential.domain if self.credential else "",
        )
        yield ActionButtons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ID_CONFIRM_BUTTON:
            self.credential = Credential(
                id=self.credential.id if self.credential else "",
                username=self.screen.query_one(f"#{ID_USERNAME_INPUT}", Input).value,
                password=self.screen.query_one(f"#{ID_PASSWORD_INPUT}", Input).value,
                hash=self.screen.query_one(f"#{ID_HASH_INPUT}", Input).value,
                domain=self.screen.query_one(f"#{ID_DOMAIN_INPUT}", Input).value,
            )

            self.screen.dismiss([self.credential])
