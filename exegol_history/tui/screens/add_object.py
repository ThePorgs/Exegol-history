from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import TabbedContent, TabPane
from textual.containers import Container
from exegol_history.tui.widgets.credential_form import CredentialForm
from exegol_history.tui.widgets.host_form import HostForm
from exegol_history.tui.widgets.import_file import AssetsType, ImportFile


class AddObjectScreen(ModalScreen):
    def __init__(
        self,
        asset_type: AssetsType = AssetsType.Credentials,
        id: str = None,
        domains: list[str] = [],
    ):
        super().__init__(id=id)
        self.asset_type = asset_type
        self.domains = domains

    def compose(self) -> ComposeResult:
        container = Container()
        container.border_title = (
            f"{self.app.config['theme']['add_icon']} Adding an object"
        )
        form = (
            CredentialForm(domains=self.domains)
            if self.asset_type == AssetsType.Credentials
            else HostForm()
        )

        with container:
            with TabbedContent():
                with TabPane("Add a single object"):
                    yield form
                with TabPane("Import from file"):
                    yield ImportFile(self.asset_type)
