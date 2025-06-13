from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.tui.widgets.delete_objects import DeleteObjects
from textual.widgets import Static

"""
This screen is used to delete the selected credential
"""


class DeleteCredentialConfirmationScreen(ModalScreen):
    def __init__(self, ids: list[int]):
        super().__init__()
        self.ids = ids

    def compose(self) -> ComposeResult:
        yield Static("Deleting a credential", id="delete_modal_title")
        yield DeleteObjects(id="delete_modal", ids=self.ids)
