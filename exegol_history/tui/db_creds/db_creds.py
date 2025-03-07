import sys

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Rule
from textual.binding import Binding
from textual.containers import Vertical
from textual import events
from pykeepass import PyKeePass
from typing import Any

from exegol_history.db_api.creds import (
    add_credential,
    get_credentials,
    delete_credential,
    edit_credential,
)
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.db_creds.add_credential import AddCredentialScreen
from exegol_history.tui.db_creds.edit_credential import EditCredentialScreen
from exegol_history.tui.db_creds.delete_credential import (
    DeleteCredentialConfirmationScreen,
)

CREDS_COLUMNS = ["Username", "Password", "Hash", "Domain"]

"""
This is the main application displaying the credentials table and a search bar
"""


class DbCredsApp(App):
    BINDINGS = [
        Binding(
            "f1",
            "copy_username_clipboard",
            " username",
            id="copy_username_clipboard",
            tooltip="Copy the username to the clipboard.",
        ),
        Binding(
            "f2",
            "copy_password_clipboard",
            " password",
            id="copy_password_clipboard",
            tooltip="Copy the password to the clipboard.",
        ),
        Binding(
            "f3",
            "copy_hash_clipboard",
            " hash",
            id="copy_hash_clipboard",
            tooltip="Copy the hash to the clipboard.",
        ),
        Binding(
            "f4",
            "add_credential",
            "+ credential",
            id="add_credential",
            tooltip="Add a credential.",
        ),
        Binding(
            "f5",
            "delete_credential",
            " credential",
            id="delete_credential",
            tooltip="Delete a credential.",
        ),
        Binding(
            "f6",
            "edit_credential",
            " credential",
            id="edit_credential",
            tooltip="Edit a credential.",
        ),
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
    ]

    def update_table(self) -> None:
        # Refresh the table
        tmp = get_credentials(self.kp)

        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(tmp)
        self.original_data = tmp

    def __init__(self, config: dict[str, Any], kp: PyKeePass):
        super().__init__()
        self.config = config
        self.kp = kp

    def compose(self) -> ComposeResult:
        yield self.main_view()

    def on_mount(self) -> None:
        tmp = get_credentials(self.kp)

        table = self.query_one(DataTable)
        table.add_columns(*CREDS_COLUMNS)
        table.add_rows(tmp)
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.original_data = tmp

        # Apply keybindings from config
        self.set_keymap(self.config["keybindings"])

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            try:
                table = self.query_one(DataTable)
                selected_row = table.cursor_row
                row_data = table.get_row_at(selected_row)
                self.exit(row_data)
            except Exception:
                pass

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            """Filter the DataTable when the search bar input changes."""
            search_query = event.value.lower()  # Case-insensitive search
            data_table = self.query_one(DataTable)

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
        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            username = row_data[0]
            copy_in_clipboard(username)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_password_clipboard(self) -> None:
        table = self.query_one(DataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            password = row_data[1]
            copy_in_clipboard(password)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_hash_clipboard(self) -> None:
        table = self.query_one(DataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            hash = row_data[2]
            copy_in_clipboard(hash)
        except Exception:
            pass

        sys.exit(0)

    def action_add_credential(self) -> None:
        def check_added_creds(parsed_creds: []) -> None:
            for cred in parsed_creds:
                add_credential(self.kp, cred[0], cred[1], cred[2], cred[3])

            self.update_table()

        self.push_screen(AddCredentialScreen(), check_added_creds)

    def action_delete_credential(self) -> None:
        def check_delete(delete: bool) -> None:
            if delete:
                table = self.query_one(DataTable)
                selected_row = table.cursor_row

                try:
                    row_data = table.get_row_at(selected_row)
                    delete_credential(self.kp, row_data[0])
                    self.update_table()
                except Exception:
                    pass

        self.push_screen(DeleteCredentialConfirmationScreen(), check_delete)

    def action_edit_credential(self) -> None:
        def check_edit_creds(creds: (str, str, str, str, str)) -> None:
            edit_credential(self.kp, creds[0], creds[1], creds[2], creds[3], creds[4])

            self.update_table()

        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            self.push_screen(
                EditCredentialScreen(
                    row_data[0], row_data[1], row_data[2], row_data[3]
                ),
                check_edit_creds,
            )
        except Exception:
            pass

    def main_view(self) -> Vertical:
        """Return the main view layout."""
        return Vertical(
            Header(),
            DataTable(),
            Rule(line_style="heavy"),
            Input(placeholder="Search...", id="search-bar"),
            Footer(),
        )
