from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.db_api.hosts import Host
from exegol_history.tui.widgets.host_form import HostForm
from textual.widgets import Static

"""
This screen is used to edit hosts informations such as the username, password, ...
"""


class EditHostScreen(ModalScreen):
    def __init__(self, host: Host):
        super().__init__()
        self.host = host

    def compose(self) -> ComposeResult:
        yield Static("Editing a host", id="add_modal_title")
        yield HostForm(self.host, id="modal")
