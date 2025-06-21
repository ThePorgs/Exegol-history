import pathlib
from textual import on
from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.db_api.exporting import CredsExportFileType, HostsExportFileType
from exegol_history.db_api.importing import CredsImportFileType, HostsImportFileType
from exegol_history.tui.widgets.action_buttons import ActionButtons
from exegol_history.tui.widgets.import_file import AssetsType
from textual.containers import Container, Horizontal
from textual.widgets import (
    Button,
    Select,
    Input,
)

from exegol_history.tui.screens.open_file import OpenFileScreen

ID_CONFIRM_BUTTON = "confirm_button"
ID_BROWSE_BUTTON = "browse_button"

ID_PATH_INPUT = "path_input"

ID_EXPORT_TYPE_SELECT = "export_type_select"

ID_BROWSE_HORIZONTAL = "browse_horizontal"


class ExportObjectScreen(ModalScreen):
    def __init__(self, asset_type: AssetsType = AssetsType.Credentials):
        super().__init__()
        self.asset_type = asset_type
        self.selected_format = (
            CredsExportFileType.CSV
            if asset_type is AssetsType.Credentials
            else HostsExportFileType.CSV
        )

    def compose(self) -> ComposeResult:
        container = Container()
        container.border_title = "📤 Exporting objects"
        options = [
            (asset_type.name, asset_type.value)
            for asset_type in (
                HostsExportFileType
                if self.asset_type == AssetsType.Hosts
                else CredsExportFileType
            )
        ]
        with container:
            yield Horizontal(
                Input(placeholder="Export path", id=ID_PATH_INPUT),
                Button(" Browse", variant="primary", id=ID_BROWSE_BUTTON),
                id=ID_BROWSE_HORIZONTAL,
            )
            yield Select(
                options,
                value=1,
                allow_blank=False,
                prompt="Select an export format",
                id=ID_EXPORT_TYPE_SELECT,
            )
            yield ActionButtons()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        def openfile_callback(path: str):
            path_tmp = pathlib.Path(path)
            if path_tmp.is_dir():
                path_tmp = path_tmp / f"output.{self.selected_format.name.lower()}"

            self.screen.query_one(f"#{ID_PATH_INPUT}", Input).value = str(path_tmp)

        if event.button.id in ID_BROWSE_BUTTON:
            self.app.push_screen(
                OpenFileScreen("Choose an export path:"), openfile_callback
            )

        if event.button.id in ID_CONFIRM_BUTTON:
            self.screen.dismiss(
                (
                    self.selected_format,
                    self.screen.query_one(f"#{ID_PATH_INPUT}", Input).value,
                )
            )
        else:
            self.screen.dismiss(None)

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if self.asset_type is AssetsType.Credentials:
            self.selected_format = CredsImportFileType(event.value)
        else:
            self.selected_format = HostsImportFileType(event.value)
