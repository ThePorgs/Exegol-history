from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import TabbedContent, TabPane, Static
from exegol_history.tui.widgets.credential_form import CredentialForm
from exegol_history.tui.widgets.import_file import AssetsType, ImportFile

"""
This screen is used to add a credential
"""


class AddCredentialScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Static("Adding a credential", id="add_modal_title")
        with TabbedContent(id="add_modal"):
            with TabPane("Add a single credential"):
                yield CredentialForm()
            with TabPane("Import from file"):
                yield ImportFile(AssetsType.Credentials)
