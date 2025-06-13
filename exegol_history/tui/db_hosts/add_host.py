from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import TabbedContent, TabPane, Static
from exegol_history.tui.widgets.host_form import HostForm
from exegol_history.tui.widgets.import_file import AssetsType, ImportFile

"""
This screen is used to add a host
"""


class AddHostScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Static("Adding a host", id="add_modal_title")
        with TabbedContent(id="add_modal"):
            with TabPane("Add a single host"):
                yield HostForm()
            with TabPane("Import from file"):
                yield ImportFile(AssetsType.Hosts)
