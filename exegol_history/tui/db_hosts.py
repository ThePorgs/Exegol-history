import importlib
import sys

from sqlalchemy import Engine
from textual import events, work
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.keys import Keys
from textual.screen import Screen
from textual.theme import Theme
from textual.widgets import Footer, Header, Input, Rule
from textual.widgets.data_table import RowDoesNotExist

from exegol_history.config.config import AppConfig
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.hosts import (
    Host,
    add_hosts,
    delete_hosts,
    edit_hosts,
    get_hosts,
)
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable
from exegol_history.tui.widgets.search_input import SearchInput

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
    # We can't reuse the config passed in the constructor
    # because Textualize doesn't support fully dynamic bindings
    config = AppConfig()
    BINDINGS = [
        Binding(
            Keys.F1,
            "copy_ip_clipboard",
            f"{config.theme.clipboard_icon} IP",
            id="copy_ip_clipboard",
            tooltip="Copy the IP to the clipboard.",
        ),
        Binding(
            Keys.F2,
            "copy_hostname_clipboard",
            f"{config.theme.clipboard_icon} hostname",
            id="copy_hostname_clipboard",
            tooltip="Copy the hostname to the clipboard.",
        ),
        Binding(
            Keys.F3,
            "add_host",
            f"{config.theme.add_icon} host",
            id="add_host",
            tooltip="Add a host.",
        ),
        Binding(
            Keys.F4,
            "delete_host",
            f"{config.theme.delete_icon} host",
            id="delete_host",
            tooltip="Delete a host.",
        ),
        Binding(
            Keys.F5,
            "edit_host",
            f"{config.theme.edit_icon} host",
            id="edit_host",
            tooltip="Edit a host.",
        ),
        Binding(
            Keys.F6,
            "export_host",
            f"{config.theme.export_icon} host",
            id="export_host",
            tooltip=TOOLTIP_EXPORT_HOST,
        ),
        Binding(Keys.ControlC, "quit", "Quit", show=False, priority=True),
    ]

    def __init__(
        self,
        config: AppConfig,
        engine: Engine,
        show_add_screen: bool = False,
        background_sync: bool = False,
    ):
        self.CSS_PATH = "css/general.tcss"
        self.TITLE = (
            f"🔑 Exegol-history v{importlib.metadata.version('exegol-history')}"
        )
        super().__init__()
        self.config = config
        self.engine = engine
        self.custom_theme = Theme(
            name="custom",
            primary=config.theme.primary,
            secondary=config.theme.secondary,
            accent=config.theme.accent,
            foreground=config.theme.foreground,
            background=config.theme.background,
            success=config.theme.success,
            warning=config.theme.warning,
            error=config.theme.error,
            surface=config.theme.surface,
            panel=config.theme.panel,
            dark=config.theme.dark,
        )
        self.show_add_screen = show_add_screen
        self.background_sync = background_sync
        self.original_data: list = []
        self._search_index: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield ObjectsDataTable()
        yield Rule(line_style="heavy")
        yield SearchInput(placeholder="🔍 Search...", id="search-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.register_theme(self.custom_theme)
        self.theme = "custom"
        tmp = get_hosts(self.engine)

        _tmp = Host()
        delattr(_tmp, "_sa_instance_state")

        table = self.screen.query_one(ObjectsDataTable)
        table.add_columns(*_tmp.__dict__.keys())
        table.add_rows(tmp)
        self._set_data(tmp)

        # Apply keybindings from config
        self.set_keymap(self.config.keybindings)

        self.query_one(SearchInput).focus()

        if self.show_add_screen:
            from exegol_history.tui.screens.add_object import AddObjectScreen
            from exegol_history.tui.widgets.import_file import AssetsType

            self.push_screen(AddObjectScreen(AssetsType.Hosts), self.check_added_host)

        if self.background_sync:
            self.sync_connectors()

    @work(thread=True, exclusive=True, group="sync", exit_on_error=False)
    def sync_connectors(self) -> None:
        """Pull NetExec / Metasploit hosts without blocking the UI."""
        from exegol_history.db_api.sync import sync_objects

        try:
            sync_objects(self.engine, self.config, True, True)
        except Exception:
            return
        self.call_from_thread(self._refresh_after_sync)

    def _refresh_after_sync(self) -> None:
        try:
            self.update_table()
        except Exception:
            # e.g. a modal screen is on top: data will be refreshed on next update
            pass

    def _set_data(self, data: list) -> None:
        self.original_data = data
        # Pre-compute the lowercase searchable text once, instead of on every keystroke
        self._search_index = [
            "\0".join(str(cell).lower() for cell in row) for row in data
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
        tmp = get_hosts(self.engine)

        table = self.screen.query_one(ObjectsDataTable)
        search_query = self.screen.query_one("#search-bar", Input).value
        self._set_data(tmp)
        if search_query:
            self._filter_table(search_query)
        else:
            table.clear()
            table.add_rows(tmp)

    def on_key(self, event: events.Key) -> Host:
        if event.key == Keys.Enter:
            try:
                table = self.screen.query_one(ObjectsDataTable)
                selected_row = table.cursor_row
                row_data = table.get_row_at(selected_row)
                select_host = get_hosts(self.engine, host_id=row_data[0])[0]

                self.exit(select_host)
            except Exception:
                pass

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the DataTable when the search bar input changes."""
        try:
            self._filter_table(event.value)
        except Exception:
            pass

    def _filter_table(self, query: str) -> None:
        search_query = query.lower()  # Case-insensitive search
        data_table = self.screen.query_one(ObjectsDataTable)

        filtered_data = [
            row
            for row, haystack in zip(self.original_data, self._search_index)
            if search_query in haystack
        ]

        data_table.clear()
        data_table.add_rows([tuple(map(str, row)) for row in filtered_data])

    def action_copy_ip_clipboard(self) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row
        try:
            row_data = table.get_row_at(selected_row)
            ip = row_data[1]
            copy_in_clipboard(ip)
        except Exception:
            pass

        sys.exit(0)

    def action_copy_hostname_clipboard(self) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            hostname = row_data[2]
            copy_in_clipboard(hostname)
        except Exception:
            pass

        sys.exit(0)

    def check_added_host(self, parsed_hosts: list[Host]) -> None:
        add_hosts(self.engine, parsed_hosts)

        self.update_table()

        if self.show_add_screen:
            sys.exit(0)

    def check_export_host(self, result: tuple) -> None:
        if result:
            format = result[0]
            export_path = result[1]

            if export_path:
                try:
                    exported = export_objects(format, get_hosts(self.engine))

                    # Reference: https://docs.python.org/3/library/csv.html#id4
                    with open(export_path, "w", newline="") as f:
                        f.write(exported)

                    self.notify("Hosts successfully exported !", severity="information")
                except Exception as e:
                    self.notify(
                        f"There was an error while exporting: {e}", severity="error"
                    )

    def action_export_host(self) -> None:
        from exegol_history.tui.screens.export_object import ExportObjectScreen
        from exegol_history.tui.widgets.import_file import AssetsType

        self.push_screen(ExportObjectScreen(AssetsType.Hosts), self.check_export_host)

    def action_add_host(self) -> None:
        from exegol_history.tui.screens.add_object import AddObjectScreen
        from exegol_history.tui.widgets.import_file import AssetsType

        self.push_screen(AddObjectScreen(AssetsType.Hosts), self.check_added_host)

    def action_delete_host(self) -> None:
        from exegol_history.tui.screens.delete_object import DeleteObjectScreen

        def check_delete(result: list[int]) -> None:
            for id in result:
                try:
                    delete_hosts(self.engine, [id])
                except RuntimeError:
                    pass

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

    def action_edit_host(self) -> None:
        from exegol_history.tui.screens.edit_object import EditObjectScreen
        from exegol_history.tui.widgets.import_file import AssetsType

        def check_edit_host(host: Host) -> None:
            try:
                edit_hosts(self.engine, [host])
            except RuntimeError as e:
                self.notify(f"There was an error while editing: {e}", severity="error")

            self.update_table()

        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            host = get_hosts(self.engine, host_id=row_data[0])[0]
            self.push_screen(
                EditObjectScreen(AssetsType.Hosts, host),
                check_edit_host,
            )
        except Exception:
            pass
