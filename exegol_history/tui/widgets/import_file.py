from enum import Enum
from textual import on
from textual.app import ComposeResult
from textual.widgets import Button, Static, TextArea, Select, Input
from textual.containers import Horizontal, Container
from exegol_history.db_api.importing import (
    CredsImportFileType,
    HostsImportFileType,
    import_objects,
)
from exegol_history.tui.screens.open_file import OpenFileScreen
from rich.markdown import Markdown

TOOLTIP_CSV = Markdown("""
Here is examples of CSV files that can be imported:
```csv
username,password,hash,domain
svc_veeam
administrator,12345,,test.local
```

```csv
ip,hostname,role
127.0.0.1
127.0.0.22,test.local,DC
```

> The CSV header is mandatory. 
""")

TOOLTIP_JSON = Markdown("""
Here is examples of JSON files that can be imported:
```json
[
  {
    "username": "administrator",
    "password": "12345",
    "hash": "",
    "domain": "test.local"
  }
]
```

```json
[
  {
    "ip": "127.0.0.1",
    "hostname": "test.local",
    "role": "DC"
  }
]
```
""")


class AssetsType(Enum):
    Credentials = "credentials"
    Hosts = "hosts"


ID_KDBX_PASSWORD_INPUT = "kdbx_password_input"
ID_KDBX_KEYFILE_INPUT = "kdbx_keyfile_input"

ID_FILE_TYPE_SELECT = "file_type_select"

ID_FILE_TEXTAREA = "file_textarea"

ID_ACTIONS_HORIZONTAL = "actions_horizontal"
ID_KDBX_KEYFILE_HORIZONTAL = "kdbx_keyfile_horizontal"

ID_CONFIRM_IMPORT_BUTTON = "confirm_import_button"
ID_CANCEL_BUTTON = "cancel_button"
ID_IMPORT_BUTTON = "import_file"
ID_KDBX_KEYFILE_BUTTON = "kdbx_keyfile_button"


class ImportFile(Container):
    def __init__(self, import_type: AssetsType):
        super().__init__()
        self.import_type = import_type
        self.selected_format: CredsImportFileType | HostsImportFileType = 0
        self.file_content = None
        self.kdbx_keyfile_path = ""

    def compose(self) -> ComposeResult:
        options = [
            (asset_type.name, asset_type.value)
            for asset_type in (
                HostsImportFileType
                if self.import_type == AssetsType.Hosts
                else CredsImportFileType
            )
        ]
        kdbx_password_input = Input(
            placeholder="KDBX Password", id=ID_KDBX_PASSWORD_INPUT, password=True
        )
        kdbx_password_input.visible = False
        kdbx_keyfile_input = Input(
            placeholder="KDBX Keyfile path", id=ID_KDBX_KEYFILE_INPUT
        )

        kdbx_keyfile_horizontal = Horizontal(
            kdbx_keyfile_input,
            Button(" Browse", variant="primary", id=ID_KDBX_KEYFILE_BUTTON),
            id=ID_KDBX_KEYFILE_HORIZONTAL,
        )
        kdbx_keyfile_horizontal.visible = False

        yield Static("Either import a file, or directly paste:")
        yield TextArea.code_editor(id=ID_FILE_TEXTAREA, tooltip=TOOLTIP_CSV)
        yield Select(
            options,
            value=1,
            allow_blank=False,
            prompt="Select an import format",
            id=ID_FILE_TYPE_SELECT,
        )
        yield kdbx_password_input
        yield kdbx_keyfile_horizontal
        yield Horizontal(
            Button.success("Confirm", id=ID_CONFIRM_IMPORT_BUTTON),
            Button.error("Cancel", id=ID_CANCEL_BUTTON),
            Button("Import", variant="primary", id=ID_IMPORT_BUTTON),
            id=ID_ACTIONS_HORIZONTAL,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == ID_IMPORT_BUTTON:

            def check_import(path: str):
                with open(path, "rb") as f:
                    self.file_content = f.read()

                self.screen.query_one(TextArea).text = (
                    self.file_content.decode("utf-8")
                    if not self.is_kdbx_format()
                    else ""
                )

            self.app.push_screen(OpenFileScreen("Choose an import path:"), check_import)
        elif event.button.id == ID_CONFIRM_IMPORT_BUTTON:
            delimiter_input = self.screen.query_one(f"#{ID_KDBX_PASSWORD_INPUT}", Input)
            kdbx_password = delimiter_input.value

            try:
                tmp = (
                    self.screen.query_one(TextArea).text.encode("utf-8")
                    if self.screen.query_one(TextArea).text
                    else self.file_content
                )

                parsed_assets = import_objects(
                    self.selected_format,
                    tmp,
                    kdbx_password=kdbx_password,
                    keyfile_path=self.kdbx_keyfile_path,
                )

                if not parsed_assets:
                    self.notify(
                        "No objects were succesfully parsed", severity="warning"
                    )
                else:
                    self.screen.dismiss(parsed_assets)
            except Exception as e:
                self.notify(f"{e}", title="Error parsing the content", severity="error")
                pass
        elif event.button.id == ID_KDBX_KEYFILE_BUTTON:

            def check_import(path: str):
                self.kdbx_keyfile_path = path
                self.screen.query_one(f"#{ID_KDBX_KEYFILE_INPUT}", Input).value = path

            self.app.push_screen(
                OpenFileScreen("Choose the KDBX keyfile location:"), check_import
            )
        elif event.button.id == ID_CANCEL_BUTTON:
            self.app.pop_screen()

    def is_kdbx_format(self):
        return self.selected_format == CredsImportFileType.KDBX

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if event.select.id == ID_FILE_TYPE_SELECT:
            if self.import_type is AssetsType.Credentials:
                self.selected_format = CredsImportFileType(event.value)
            else:
                self.selected_format = HostsImportFileType(event.value)

            file_text_area = self.screen.query_one(TextArea)
            if self.selected_format in (
                CredsImportFileType.JSON,
                HostsImportFileType.JSON,
            ):
                file_text_area.tooltip = TOOLTIP_JSON
            elif self.selected_format in (
                CredsImportFileType.CSV,
                HostsImportFileType.CSV,
            ):
                file_text_area.tooltip = TOOLTIP_CSV
            else:
                file_text_area.tooltip = None

            kdbx_password_input = self.screen.query_one(
                f"#{ID_KDBX_PASSWORD_INPUT}", Input
            )
            kdbx_keyfile_horizontal = self.screen.query_one(
                f"#{ID_KDBX_KEYFILE_HORIZONTAL}", Horizontal
            )
            kdbx_password_input.visible = kdbx_keyfile_horizontal.visible = (
                self.is_kdbx_format()
            )
