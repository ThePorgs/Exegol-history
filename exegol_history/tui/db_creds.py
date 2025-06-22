import sys
import importlib
from textual.app import App, ComposeResult, SystemCommand
from textual.keys import Keys
from textual.screen import Screen
from textual.widgets.data_table import RowDoesNotExist
from textual.widgets import Footer, Header, Input, Rule
from textual.binding import Binding
from textual import events
from pykeepass import PyKeePass
from typing import Any
from exegol_history.config.config import load_config
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    delete_credential,
    edit_credentials,
    get_credentials,
)
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.screens.add_object import AddObjectScreen
from exegol_history.tui.screens.delete_object import DeleteObjectScreen
from exegol_history.tui.screens.edit_object import EditObjectScreen
from exegol_history.tui.screens.export_object import ExportObjectScreen
from exegol_history.tui.widgets.import_file import AssetsType
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable

"""
This is the main application displaying the credentials table and a search bar
"""

TOOLTIP_COPY_USERNAME = "Copy the username to the clipboard"
TOOLTIP_COPY_PASSWORD = "Copy the password to the clipboard"
TOOLTIP_COPY_HASH = "Copy the password to the clipboard"
TOOLTIP_ADD_CREDENTIAL = "Add a new credential"
TOOLTIP_DELETE_CREDENTIAL = "Delete the selected credential or multiple credentials"
TOOLTIP_EDIT_CREDENTIAL = "Edit the selected credential"
TOOLTIP_EXPORT_CREDENTIAL = "Export credentials"


class DbCredsApp(App):
    # We can't reuse the config passed in the constructor
    # because Textualize doesn't support fully dynamic bindings
    config = load_config()
    BINDINGS = [
        Binding(
            Keys.F1,
            "copy_username_clipboard",
            f"{config['theme']['clipboard_icon']} username",
            id="copy_username_clipboard",
            tooltip=TOOLTIP_COPY_USERNAME,
        ),
        Binding(
            Keys.F2,
            "copy_password_clipboard",
            f"{config['theme']['clipboard_icon']} password",
            id="copy_password_clipboard",
            tooltip=TOOLTIP_COPY_PASSWORD,
        ),
        Binding(
            Keys.F3,
            "copy_hash_clipboard",
            f"{config['theme']['clipboard_icon']} hash",
            id="copy_hash_clipboard",
            tooltip=TOOLTIP_COPY_HASH,
        ),
        Binding(
            Keys.F4,
            "add_credential",
            f"{config['theme']['add_icon']} credential",
            id="add_credential",
            tooltip=TOOLTIP_ADD_CREDENTIAL,
        ),
        Binding(
            Keys.F5,
            "delete_credential",
            f"{config['theme']['delete_icon']} credential",
            id="delete_credential",
            tooltip=TOOLTIP_DELETE_CREDENTIAL,
        ),
        Binding(
            Keys.F6,
            "edit_credential",
            f"{config['theme']['edit_icon']} credential",
            id="edit_credential",
            tooltip=TOOLTIP_EDIT_CREDENTIAL,
        ),
        Binding(
            Keys.F7,
            "export_credential",
            f"{config['theme']['export_icon']} credential",
            id="export_credential",
            tooltip=TOOLTIP_EXPORT_CREDENTIAL,
        ),
        Binding(Keys.ControlC, "quit", "Quit", show=False, priority=True),
    ]

    def __init__(
        self, config: dict[str, Any], kp: PyKeePass, show_add_screen: bool = False
    ):
        self.CSS_PATH = "css/general.tcss"
        self.TITLE = f"🔑 Exegol-history v{importlib.metadata.version('exegol-history')}"
        super().__init__()

        self.config = config
        self.refresh_bindings()
        self.kp = kp
        self.show_add_screen = show_add_screen

    def compose(self) -> ComposeResult:
        yield Header()
        yield ObjectsDataTable()
        yield Rule(line_style="heavy")
        yield Input(placeholder="🔍 Search...", id="search-bar")
        yield Footer()

    def on_mount(self) -> None:
        tmp = get_credentials(self.kp)

        _tmp = Credential()

        table = self.screen.query_one(ObjectsDataTable)
        table.add_columns(*_tmp.__dict__.keys())
        table.add_rows(tmp)
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.original_data = tmp

        # Apply keybindings from config
        self.set_keymap(self.config["keybindings"])

        if self.show_add_screen:
            self.push_screen(AddObjectScreen(), self.check_added_creds)

    def get_system_commands(self, screen: Screen):
        yield SystemCommand(
            "Copy username", TOOLTIP_COPY_USERNAME, self.action_copy_username_clipboard
        )
        yield SystemCommand(
            "Copy password", TOOLTIP_COPY_PASSWORD, self.action_copy_password_clipboard
        )
        yield SystemCommand(
            "Copy hash", TOOLTIP_COPY_HASH, self.action_copy_hash_clipboard
        )
        yield SystemCommand(
            "Add credential", TOOLTIP_ADD_CREDENTIAL, self.action_add_credential
        )
        yield SystemCommand(
            "Delete credential",
            TOOLTIP_DELETE_CREDENTIAL,
            self.action_delete_credential,
        )
        yield SystemCommand(
            "Edit credential", TOOLTIP_EDIT_CREDENTIAL, self.action_edit_credential
        )
        yield SystemCommand(
            "Export credentials", TOOLTIP_EDIT_CREDENTIAL, self.action_export_credential
        )

    def update_table(self) -> None:
        # Refresh the table
        tmp = get_credentials(self.kp)

        table = self.screen.query_one(ObjectsDataTable)
        table.clear()
        table.add_rows(tmp)
        self.original_data = tmp

    def on_key(self, event: events.Key) -> Credential:
        if event.key == Keys.Enter:
            try:
                table = self.screen.query_one(ObjectsDataTable)
                selected_row = table.cursor_row
                row_data = table.get_row_at(selected_row)
                select_credential = get_credentials(self.kp, id=row_data[0])[0]
                self.exit(select_credential)
            except Exception:
                pass

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            """Filter the DataTable when the search bar input changes."""
            search_query = event.value.lower()  # Case-insensitive search
            data_table = self.screen.query_one(ObjectsDataTable)

            # Clear current rows
            data_table.clear()

            # Filter rows based on the search query
            filtered_data = [
                row
                for row in self.original_data
                if any(search_query in str(cell).lower() for cell in row)
            ]

            # Add filtered rows back to the DataTable
            for row in filtered_data:
                data_table.add_row(*map(str, row))
        except Exception:
            pass

    def action_copy_username_clipboard(self) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            username = row_data[1]
            copy_in_clipboard(username)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_password_clipboard(self) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            password = row_data[2]
            copy_in_clipboard(password)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_hash_clipboard(self) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            hash = row_data[3]
            copy_in_clipboard(hash)
        except Exception:
            pass

        sys.exit(0)

    def check_added_creds(self, parsed_creds: list[Credential]) -> None:
        add_credentials(self.kp, parsed_creds)
        self.update_table()

        if self.show_add_screen:
            sys.exit(0)

    def action_add_credential(self) -> None:
        self.push_screen(AddObjectScreen(), self.check_added_creds)

    def check_export_credential(self, result: tuple) -> None:
        if result:
            format = result[0]
            export_path = result[1]

            if export_path:
                try:
                    exported = export_objects(format, get_credentials(self.kp))

                    # Reference: https://docs.python.org/3/library/csv.html#id4
                    with open(export_path, "w", newline="") as f:
                        f.write(exported)

                    self.notify(
                        "Credentials successfully exported !", severity="information"
                    )
                except Exception as e:
                    self.notify(
                        f"There was an error while exporting: {e}", severity="error"
                    )

    def action_export_credential(self) -> None:
        self.push_screen(ExportObjectScreen(), self.check_export_credential)

    def action_delete_credential(self) -> None:
        def check_delete(result: list[int]) -> None:
            for id in result:
                try:
                    delete_credential(self.kp, id)
                except RuntimeError:
                    continue

            self.kp.save()
            self.update_table()

        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            self.push_screen(
                DeleteObjectScreen([table.get_row_at(selected_row)[0]]),
                check_delete,
            )
        except RowDoesNotExist:
            pass

    def action_edit_credential(self) -> None:
        def check_edit_creds(credentials: list[Credential]) -> None:
            edit_credentials(self.kp, credentials)

            self.update_table()

        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            credential = get_credentials(self.kp, id=row_data[0])[0]
            self.push_screen(
                EditObjectScreen(AssetsType.Credentials, credential),
                check_edit_creds,
            )
        except Exception:
            pass
