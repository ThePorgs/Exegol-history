from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.db_api.creds import Credential
from exegol_history.tui.widgets.credential_form import CredentialForm
from textual.widgets import Static

"""
This screen is used to edit credentials informations such as the username, password, ...
"""


class EditCredentialScreen(ModalScreen):
    def __init__(self, credential: Credential):
        super().__init__()
        self.credential = credential

    def compose(self) -> ComposeResult:
        yield Static("Editing a credential", id="add_modal_title")
        yield CredentialForm(self.credential, id="modal")
