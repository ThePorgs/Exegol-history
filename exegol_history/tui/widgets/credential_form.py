from textual.app import ComposeResult
from textual.widgets import Button
from textual.suggester import SuggestFromList
from textual.containers import (
    Container,
)
from exegol_history.db_api.creds import Credential
from exegol_history.tui.widgets.action_buttons import ActionButtons
from exegol_history.tui.widgets.bordered_inputs import BorderedInput

ID_USERNAME_INPUT = "username_input"
ID_PASSWORD_INPUT = "password_input"
ID_HASH_INPUT = "hash_input"
ID_DOMAIN_INPUT = "domain_input"

ID_ACTIONS_HORIZONTAL = "actions_horizontal"
ID_LIMITED_HORIZONTAL = "limited_horizontal"

ID_CONFIRM_BUTTON = "confirm_button"
ID_CANCEL_BUTTON = "cancel_button"


class CredentialForm(Container):
    def __init__(
        self, credential: Credential = None, id: str = None, domains: list[str] = []
    ):
        super().__init__(id=id)
        self.domains = domains
        self.credential = credential
        self.button_clicked = None

    def compose(self) -> ComposeResult:
        yield BorderedInput(
            "Username",
            placeholder="Administrator",
            id=ID_USERNAME_INPUT,
            value=self.credential.username if self.credential else "",
        )
        yield BorderedInput(
            "Password",
            placeholder="Password123!",
            id=ID_PASSWORD_INPUT,
            value=self.credential.password if self.credential else "",
        )
        yield BorderedInput(
            "Hash",
            placeholder="b4b9b02e6f09a9bd760f388b67351e2b",
            id=ID_HASH_INPUT,
            value=self.credential.hash if self.credential else "",
        )
        yield BorderedInput(
            "Domain",
            placeholder="example.local",
            id=ID_DOMAIN_INPUT,
            value=self.credential.domain if self.credential else "",
            suggester=SuggestFromList(self.domains, case_sensitive=False),
        )
        yield ActionButtons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ID_CONFIRM_BUTTON:
            self.credential = Credential(
                id=self.credential.id if self.credential else "",
                username=self.screen.query_one(
                    f"#{ID_USERNAME_INPUT}", BorderedInput
                ).value,
                password=self.screen.query_one(
                    f"#{ID_PASSWORD_INPUT}", BorderedInput
                ).value,
                hash=self.screen.query_one(f"#{ID_HASH_INPUT}", BorderedInput).value,
                domain=self.screen.query_one(
                    f"#{ID_DOMAIN_INPUT}", BorderedInput
                ).value,
            )

            self.screen.dismiss([self.credential])
