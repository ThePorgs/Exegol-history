import importlib.metadata

from sqlalchemy import Engine
from textual import events, on
from textual.app import App, ComposeResult
from textual.keys import Keys
from textual.theme import Theme
from textual.widgets import Footer, Header, Input, Rule
from textual.widgets.data_table import RowDoesNotExist

from exegol_history.config.config import AppConfig
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable
from exegol_history.tui.widgets.search_input import SearchInput


class TableApp(App):
    """A searchable table: theme, title, search bar, row selection and copy.
    Shared by the credentials, hosts and Kerberos apps."""

    ICON = "🔑"
    COLUMNS: tuple[str, ...] = ()

    # Textual reads BINDINGS before __init__, so they come from the default
    # config; the user's keymap is applied in on_mount.
    config = AppConfig()

    def __init__(self, config: AppConfig, engine: Engine = None):
        self.CSS_PATH = "css/general.tcss"
        self.TITLE = f"{self.ICON} Exegol-history v{importlib.metadata.version('exegol-history')}"
        super().__init__()
        self.config = config
        self.engine = engine
        self.original_data: list[tuple] = []
        self._search_index: list[str] = []
        t = config.theme
        self.custom_theme = Theme(
            name="custom",
            primary=t.primary,
            secondary=t.secondary,
            accent=t.accent,
            foreground=t.foreground,
            background=t.background,
            success=t.success,
            warning=t.warning,
            error=t.error,
            surface=t.surface,
            panel=t.panel,
            dark=t.dark,
        )

    # --- layout ---
    def compose(self) -> ComposeResult:
        yield Header()
        yield from self.compose_main()
        yield Rule(line_style="heavy")
        yield SearchInput(placeholder="🔍 Search...", id="search-bar")
        yield Footer()

    def compose_main(self) -> ComposeResult:
        yield ObjectsDataTable()

    def on_mount(self) -> None:
        # Textual calls on_mount on every class of the MRO, so subclasses must
        # not define it again: they override load_data instead.
        self.register_theme(self.custom_theme)
        self.theme = "custom"
        self.table.add_columns(*self.COLUMNS)
        self.set_keymap(self.config.keybindings)
        self.query_one(SearchInput).focus()
        self.load_data()

    def load_data(self) -> None:
        """Fill the table once the app is mounted."""

    # --- rows and search ---
    @property
    def table(self) -> ObjectsDataTable:
        # The main screen, even while a modal (add, edit...) is on top.
        return self.screen_stack[0].query_one(ObjectsDataTable)

    def set_rows(self, rows) -> None:
        self.original_data = [tuple(row) for row in rows]
        # Lowercase searchable text computed once per refresh, not per keystroke
        self._search_index = [
            "\0".join(map(str, row)).lower() for row in self.original_data
        ]
        self._filter_table(self.screen_stack[0].query_one("#search-bar", Input).value)

    def add_table_rows(self, rows) -> None:
        self.table.add_rows(rows)

    @on(Input.Changed, "#search-bar")
    def search(self, event: Input.Changed) -> None:
        self._filter_table(event.value)

    def _filter_table(self, query: str) -> None:
        query = query.lower()
        self.table.clear()
        self.add_table_rows(
            row
            for row, haystack in zip(self.original_data, self._search_index)
            if query in haystack
        )

    # --- selection ---
    def selected_row(self) -> list | None:
        try:
            return self.table.get_row_values_at(self.table.cursor_row)
        except RowDoesNotExist:
            return None

    def selected_object(self, row: list):
        """What Enter returns to the CLI for the selected row."""
        return row

    def on_key(self, event: events.Key) -> None:
        # Enter selects a row only on the main screen, not inside a modal.
        on_main_screen = self.screen is self.screen_stack[0]
        if event.key == Keys.Enter and on_main_screen and (row := self.selected_row()):
            self.exit(self.selected_object(row))

    def action_copy_column(self, column: int) -> None:
        if row := self.selected_row():
            copy_in_clipboard(row[column])
        self.exit()
