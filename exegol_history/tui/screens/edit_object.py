from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Container
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.tui.widgets.credential_form import CredentialForm
from exegol_history.tui.widgets.host_form import HostForm
from exegol_history.tui.widgets.import_file import AssetsType


class EditObjectScreen(ModalScreen):
    def __init__(
        self,
        asset_type: AssetsType = AssetsType.Credentials,
        object_to_modify: Host | Credential = None,
        id: str = None,
    ):
        super().__init__(id=id)
        self.asset_type = asset_type
        self.object_to_modify = object_to_modify

    def compose(self) -> ComposeResult:
        container = Container()
        container.border_title = "📝 Editing an object"
        form = (
            CredentialForm(self.object_to_modify)
            if self.asset_type == AssetsType.Credentials
            else HostForm(self.object_to_modify)
        )

        with container:
            yield form
