import sys
import importlib
from sqlalchemy import Engine
from textual.app import App, ComposeResult, SystemCommand
from textual.keys import Keys
from textual.theme import Theme
from textual.screen import Screen
from textual.widgets.data_table import RowDoesNotExist
from textual.widgets import Footer, Header, Input, Rule
from textual.binding import Binding
from textual import work
from textual import events
from exegol_history.config.config import AppConfig
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    delete_credentials,
    edit_credentials,
    get_credentials,
)
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable
from exegol_history.tui.widgets.search_input import SearchInput

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
    config = AppConfig()
    BINDINGS = [
        Binding(
            Keys.F1,
            "copy_username_clipboard",
            f"{config.theme.clipboard_icon} username",
            id="copy_username_clipboard",
            tooltip=TOOLTIP_COPY_USERNAME,
        ),
        Binding(
            Keys.F2,
            "copy_password_clipboard",
            f"{config.theme.clipboard_icon} password",
            id="copy_password_clipboard",
            tooltip=TOOLTIP_COPY_PASSWORD,
        ),
        Binding(
            Keys.F3,
            "copy_hash_clipboard",
            f"{config.theme.clipboard_icon} hash",
            id="copy_hash_clipboard",
            tooltip=TOOLTIP_COPY_HASH,
        ),
        Binding(
            Keys.F4,
            "add_credential",
            f"{config.theme.add_icon} credential",
            id="add_credential",
            tooltip=TOOLTIP_ADD_CREDENTIAL,
        ),
        Binding(
            Keys.F5,
            "delete_credential",
            f"{config.theme.delete_icon} credential",
            id="delete_credential",
            tooltip=TOOLTIP_DELETE_CREDENTIAL,
        ),
        Binding(
            Keys.F6,
            "edit_credential",
            f"{config.theme.edit_icon} credential",
            id="edit_credential",
            tooltip=TOOLTIP_EDIT_CREDENTIAL,
        ),
        Binding(
            Keys.F7,
            "export_credential",
            f"{config.theme.export_icon} credential",
            id="export_credential",
            tooltip=TOOLTIP_EXPORT_CREDENTIAL,
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
        self.refresh_bindings()
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
        tmp = get_credentials(self.engine)

        _tmp = Credential()
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

            self.push_screen(
                AddObjectScreen(domains=set(table.get_column_at(4))),
                self.check_added_creds,
            )

        if self.background_sync:
            self.sync_connectors()

    @work(thread=True, exclusive=True, group="sync", exit_on_error=False)
    def sync_connectors(self) -> None:
        """Pull NetExec / Metasploit credentials without blocking the UI."""
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
        tmp = get_credentials(self.engine)

        table = self.screen.query_one(ObjectsDataTable)
        search_query = self.screen.query_one("#search-bar", Input).value
        self._set_data(tmp)
        if search_query:
            self._filter_table(search_query)
        else:
            table.clear()
            table.add_rows(tmp)

    def on_key(self, event: events.Key) -> Credential:
        if event.key == Keys.Enter:
            try:
                table = self.screen.query_one(ObjectsDataTable)
                selected_row = table.cursor_row
                row_data = table.get_row_at(selected_row)
                select_credential = get_credentials(
                    self.engine, credential_id=row_data[0]
                )[0]

                self.exit(select_credential)
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

    def check_added_creds(self, credential: list[dict]) -> None:
        add_credentials(self.engine, credential)
        self.update_table()

        if self.show_add_screen:
            sys.exit(0)

    def action_add_credential(self) -> None:
        from exegol_history.tui.screens.add_object import AddObjectScreen

        table = self.screen.query_one(ObjectsDataTable)
        self.push_screen(
            AddObjectScreen(domains=set(filter(None, table.get_column_at(4)))),
            self.check_added_creds,
        )

    def check_export_credential(self, result: tuple) -> None:
        if result:
            format = result[0]
            export_path = result[1]

            if export_path:
                try:
                    exported = export_objects(format, get_credentials(self.engine))

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
        from exegol_history.tui.screens.export_object import ExportObjectScreen

        self.push_screen(ExportObjectScreen(), self.check_export_credential)

    def action_delete_credential(self) -> None:
        from exegol_history.tui.screens.delete_object import DeleteObjectScreen

        def check_delete(result: list[int]) -> None:
            for id in result:
                try:
                    delete_credentials(self.engine, [id])
                except RuntimeError:
                    continue

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
        from exegol_history.tui.screens.edit_object import EditObjectScreen
        from exegol_history.tui.widgets.import_file import AssetsType

        def check_edit_creds(credential: Credential) -> None:
            try:
                edit_credentials(self.engine, [credential])
            except RuntimeError as e:
                self.notify(f"There was an error while editing: {e}", severity="error")

            self.update_table()

        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row

        try:
            row_data = table.get_row_at(selected_row)
            credential = get_credentials(self.engine, credential_id=row_data[0])[0]
            self.push_screen(
                EditObjectScreen(
                    AssetsType.Credentials,
                    credential,
                    domains=set(filter(None, table.get_column_at(4))),
                ),
                check_edit_creds,
            )
        except Exception:
            pass
