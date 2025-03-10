import sys

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Rule
from textual.binding import Binding
from textual.containers import Vertical
from textual import events
from pykeepass import PyKeePass
from typing import Any

from exegol_history.db_api.hosts import add_host, get_hosts, delete_host, edit_host
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.db_hosts.add_host import AddHostScreen
from exegol_history.tui.db_hosts.edit_host import EditHostScreen
from exegol_history.tui.db_hosts.delete_host import DeleteHostConfirmationScreen

HOSTS_COLUMNS = ["IP", "Hostname", "Role"]

"""
This is the main application displaying the hosts table and a search bar
"""


class DbHostsApp(App):
    BINDINGS = [
        Binding(
            "f1",
            "copy_ip_clipboard",
            " IP",
            id="copy_ip_clipboard",
            tooltip="Copy the IP to the clipboard.",
        ),
        Binding(
            "f2",
            "copy_hostname_clipboard",
            " hostname",
            id="copy_hostname_clipboard",
            tooltip="Copy the hostname to the clipboard.",
        ),
        Binding("f3", "add_host", "+ host", id="add_host", tooltip="Add a host."),
        Binding(
            "f4", "delete_host", " host", id="delete_host", tooltip="Delete a host."
        ),
        Binding("f5", "edit_host", " host", id="edit_host", tooltip="Edit a host."),
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
    ]

    def update_table(self) -> None:
        # Refresh the table
        tmp = get_hosts(self.kp)

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
        tmp = get_hosts(self.kp)

        table = self.query_one(DataTable)
        table.add_columns(*HOSTS_COLUMNS)
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
            search_query = event.value.lower()
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

    def action_copy_ip_clipboard(self) -> None:
        table = self.query_one(DataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            ip = row_data[0]
            copy_in_clipboard(ip)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_hostname_clipboard(self) -> None:
        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            hostname = row_data[1]
            copy_in_clipboard(hostname)
        except Exception:
            pass

        sys.exit(0)

    def action_add_host(self) -> None:
        def check_added_host(parsed_hosts: []) -> None:
            for host in parsed_hosts:
                add_host(self.kp, host[0], host[1], host[2])

            self.update_table()

        self.push_screen(AddHostScreen(), check_added_host)

    def action_delete_host(self) -> None:
        def check_delete(delete: bool) -> None:
            if delete:
                table = self.query_one(DataTable)
                selected_row = table.cursor_row

                try:
                    row_data = table.get_row_at(selected_row)
                    delete_host(self.kp, row_data[0])
                except Exception:
                    pass

                self.update_table()

        self.push_screen(DeleteHostConfirmationScreen(), check_delete)

    def action_edit_host(self) -> None:
        def check_edit_host(host: (str, str, str, str)) -> None:
            edit_host(self.kp, host[0], host[1], host[2], host[3])

            self.update_table()

        table = self.query_one(DataTable)

        try:
            selected_row = table.cursor_row
            row_data = table.get_row_at(selected_row)
            self.push_screen(
                EditHostScreen(row_data[0], row_data[1], row_data[2]), check_edit_host
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
