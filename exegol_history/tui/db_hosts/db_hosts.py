import sys
import importlib
from textual.app import App, ComposeResult, SystemCommand
from textual.keys import Keys
from textual.screen import Screen
from textual.widgets.data_table import RowDoesNotExist
from textual.widgets import Footer, Header, DataTable, Input, Rule
from textual.binding import Binding
from textual.containers import Vertical
from textual import events
from pykeepass import PyKeePass
from typing import Any
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.hosts import (
    Host,
    add_hosts,
    delete_host,
    edit_hosts,
    get_hosts,
)
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.db_hosts.add_host import AddHostScreen
from exegol_history.tui.db_hosts.edit_host import EditHostScreen
from exegol_history.tui.db_hosts.delete_host import DeleteHostConfirmationScreen
from exegol_history.tui.db_hosts.export_host import ExportHostScreen

TOOLTIP_COPY_IP = "Copy the IP to the clipboard"
TOOLTIP_COPY_HOSTNAME = "Copy the hostname to the clipboard"
TOOLTIP_ADD_HOST = "Add a new host"
TOOLTIP_DELETE_HOST = "Delete the selected host or multiple hosts"
TOOLTIP_EDIT_HOST = "Edit the selected host"
TOOLTIP_EXPORT_HOST = "Export hosts"


"""
This is the main application displaying the hosts table and a search bar
"""


class DbHostsApp(App):
    CSS_PATH = "../css/general.tcss"
    TITLE = f"Exegol-history v{importlib.metadata.version('exegol-history')}"
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
        Binding(
            "f6",
            "export_host",
            " host",
            id="export_host",
            tooltip=TOOLTIP_EXPORT_HOST,
        ),
        Binding(Keys.ControlC, "quit", "Quit", show=False, priority=True),
    ]

    def get_system_commands(self, screen: Screen):
        yield SystemCommand("Copy IP", TOOLTIP_COPY_IP, self.action_copy_ip_clipboard)
        yield SystemCommand(
            "Copy hostname", TOOLTIP_COPY_HOSTNAME, self.action_copy_hostname_clipboard
        )
        yield SystemCommand("Add host", TOOLTIP_ADD_HOST, self.action_add_host)
        yield SystemCommand("Delete host", TOOLTIP_DELETE_HOST, self.action_delete_host)
        yield SystemCommand("Edit host", TOOLTIP_EDIT_HOST, self.action_edit_host)
        yield SystemCommand(
            "Export hosts", TOOLTIP_EXPORT_HOST, self.action_export_host
        )

    def update_table(self) -> None:
        # Refresh the table
        tmp = get_hosts(self.kp)

        table = self.query_one(DataTable)
        table.clear()
        table.add_rows(tmp)
        self.original_data = tmp

    def __init__(
        self, config: dict[str, Any], kp: PyKeePass, show_add_screen: bool = False
    ):
        super().__init__()
        self.config = config
        self.kp = kp
        self.show_add_screen = show_add_screen

    def compose(self) -> ComposeResult:
        yield Vertical(
            Header(),
            DataTable(),
            Rule(line_style="heavy"),
            Input(placeholder="Search...", id="search-bar"),
            Footer(),
        )

    def on_mount(self) -> None:
        tmp = get_hosts(self.kp)

        _tmp = Host()

        table = self.query_one(DataTable)
        table.add_columns(*_tmp.__dict__.keys())
        table.add_rows(tmp)
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.original_data = tmp

        # Apply keybindings from config
        self.set_keymap(self.config["keybindings"])

        if self.show_add_screen:
            self.push_screen(AddHostScreen(), self.check_added_host)

    def on_key(self, event: events.Key) -> Host:
        if event.key == Keys.Enter:
            try:
                table = self.query_one(DataTable)
                selected_row = table.cursor_row
                row_data = table.get_row_at(selected_row)
                self.exit(Host(row_data[0], row_data[1], row_data[2], row_data[3]))
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
            ip = row_data[1]
            copy_in_clipboard(ip)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_hostname_clipboard(self) -> None:
        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            hostname = row_data[2]
            copy_in_clipboard(hostname)
        except Exception:
            pass

        sys.exit(0)

    def check_added_host(self, parsed_hosts: list[Host]) -> None:
        add_hosts(self.kp, parsed_hosts)

        self.update_table()

        if self.show_add_screen:
            sys.exit(0)

    def check_export_host(self, result: tuple) -> None:
        if result:
            format = result[0]
            export_path = result[1]

            if export_path:
                try:
                    exported = export_objects(format, get_hosts(self.kp))

                    with open(export_path, "w") as f:
                        f.write(exported)

                    self.notify("Hosts successfully exported !", severity="information")
                except Exception as e:
                    self.notify(
                        f"There was an error while exporting: {e}", severity="error"
                    )

    def action_export_host(self) -> None:
        self.push_screen(ExportHostScreen(), self.check_export_host)

    def action_add_host(self) -> None:
        self.push_screen(AddHostScreen(), self.check_added_host)

    def action_delete_host(self) -> None:
        def check_delete(result: list[int]) -> None:
            for id in result:
                try:
                    delete_host(self.kp, id)
                except RuntimeError:
                    pass

            self.kp.save()
            self.update_table()

        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            self.push_screen(
                DeleteHostConfirmationScreen([table.get_row_at(selected_row)[0]]),
                check_delete,
            )
        except RowDoesNotExist:
            pass

    def action_edit_host(self) -> None:
        def check_edit_host(hosts: list[Host]) -> None:
            edit_hosts(self.kp, hosts)

            self.update_table()

        table = self.query_one(DataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            host = get_hosts(self.kp, id=row_data[0])[0]
            self.push_screen(
                EditHostScreen(host),
                check_edit_host,
            )
        except Exception:
            pass
