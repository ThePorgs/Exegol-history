from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.tui.widgets.export_objects import ExportObjects
from exegol_history.tui.widgets.import_file import AssetsType
from textual.widgets import Static

"""
This screen is used to export the selected host
"""


class ExportHostScreen(ModalScreen):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static("Exporting hosts", id="add_modal_title")
        yield ExportObjects(AssetsType.Hosts, id="export_modal")
