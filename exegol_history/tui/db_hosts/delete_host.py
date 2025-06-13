from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.tui.widgets.delete_objects import DeleteObjects

"""
This screen is used to delete the selected host
"""


class DeleteHostConfirmationScreen(ModalScreen):
    def __init__(self, ids: list[int]):
        super().__init__()
        self.ids = ids

    def compose(self) -> ComposeResult:
        yield DeleteObjects(id="delete_modal", ids=self.ids)
