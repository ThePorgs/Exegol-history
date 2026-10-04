import sys
import importlib
from textual.app import App, ComposeResult, SystemCommand
from textual.keys import Keys
from textual.theme import Theme
from textual.screen import Screen
from textual.widgets.data_table import RowDoesNotExist
from textual.widgets import Footer, Header, Input, Rule, Static
from textual.containers import Horizontal, VerticalScroll
from textual.binding import Binding
from exegol_history.config.config import AppConfig
from exegol_history.db_api.kerberos import (
    Ticket,
    convert_ticket,
    describe_and_enrich_tickets,
    kirbi_output_path,
    scan_ccache_tickets,
)
from exegol_history.db_api.utils import copy_in_clipboard
from exegol_history.tui.widgets.object_datatable import ObjectsDataTable

"""
This is the main application displaying the Kerberos tickets table, a search bar
and a panel describing the currently selected ticket.
"""

TOOLTIP_COPY_PATH = "Copy the ticket path to the clipboard"
TOOLTIP_CONVERT_TICKET = "Convert the selected ticket to a .kirbi file"
TOOLTIP_REFRESH_TICKETS = "Rescan the configured paths for tickets"

ID_DESCRIBE_PANEL = "describe_panel"
ID_DESCRIBE_STATIC = "describe_static"
ID_MAIN_HORIZONTAL = "main_horizontal"


class DbKerberosApp(App):
    # We can't reuse the config passed in the constructor
    # because Textualize doesn't support fully dynamic bindings
    config = AppConfig()
    BINDINGS = [
        Binding(
            Keys.F1,
            "copy_path_clipboard",
            f"{config.theme.clipboard_icon} path",
            id="copy_path_clipboard",
            tooltip=TOOLTIP_COPY_PATH,
        ),
        Binding(
            Keys.F2,
            "convert_ticket",
            "🎟️ convert",
            id="convert_ticket",
            tooltip=TOOLTIP_CONVERT_TICKET,
        ),
        Binding(
            Keys.F3,
            "refresh_tickets",
            "🔄 refresh",
            id="refresh_tickets",
            tooltip=TOOLTIP_REFRESH_TICKETS,
        ),
        Binding(Keys.ControlC, "quit", "Quit", show=False, priority=True),
    ]

    def __init__(self, config: AppConfig, engine=None):
        self.CSS_PATH = "css/general.tcss"
        self.TITLE = (
            f"🔑 Exegol-history v{importlib.metadata.version('exegol-history')}"
        )
        super().__init__()

        self.config = config
        self.refresh_bindings()
        # engine is accepted for API consistency with the other TUI apps but is
        # not needed here since tickets live on the filesystem, not in the DB.
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
        self.original_data: list[Ticket] = []
        self.tickets_by_path: dict[str, Ticket] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id=ID_MAIN_HORIZONTAL):
            yield ObjectsDataTable()
            with VerticalScroll(id=ID_DESCRIBE_PANEL):
                yield Static(
                    "Select a ticket to display its description.",
                    id=ID_DESCRIBE_STATIC,
                )
        yield Rule(line_style="heavy")
        yield Input(placeholder="🔍 Search...", id="search-bar")
        yield Footer()

    def _scan_tickets(self) -> list[Ticket]:
        # Scan for tickets, then describe them all once (filling describe_output,
        # username and domain). describeTicket.py is therefore only run here, at
        # table creation and refresh, and never live while moving the cursor.
        tickets = scan_ccache_tickets(
            self.config.kerberos.search_paths,
            self.config.kerberos.search_depth,
        )
        describe_and_enrich_tickets(
            tickets, self.config.kerberos.describe_ticket_command
        )
        return tickets

    def _set_tickets(self, tickets: list[Ticket]) -> None:
        self.original_data = tickets
        # path -> ticket lookup so the describe panel can fetch the cached output.
        self.tickets_by_path = {ticket.path: ticket for ticket in tickets}

    def on_mount(self) -> None:
        self.register_theme(self.custom_theme)
        self.theme = "custom"

        tickets = self._scan_tickets()

        table = self.screen.query_one(ObjectsDataTable)
        # Explicit column keys let us reliably update cells later on.
        table.add_column("path", key="path")
        table.add_column("username", key="username")
        table.add_column("domain", key="domain")
        self._set_tickets(tickets)
        self._populate_rows(table, tickets)

        # Apply keybindings from config
        self.set_keymap(self.config.keybindings)


    def _populate_rows(self, table: ObjectsDataTable, tickets: list[Ticket]) -> None:
        # Use the ticket path as the row key so cells can be updated by path.
        for ticket in tickets:
            table.add_row(ticket.path, ticket.username, ticket.domain, key=ticket.path)

    def get_system_commands(self, screen: Screen):
        yield SystemCommand(
            "Copy path", TOOLTIP_COPY_PATH, self.action_copy_path_clipboard
        )
        yield SystemCommand(
            "Convert ticket", TOOLTIP_CONVERT_TICKET, self.action_convert_ticket
        )
        yield SystemCommand(
            "Refresh tickets", TOOLTIP_REFRESH_TICKETS, self.action_refresh_tickets
        )

    def _get_selected_ticket(self) -> Ticket:
        table = self.screen.query_one(ObjectsDataTable)
        selected_row = table.cursor_row
        row_data = table.get_row_at(selected_row)
        return Ticket(row_data[0], row_data[1], row_data[2])

    def _show_description(self, path: str) -> None:
        describe_static = self.screen.query_one(f"#{ID_DESCRIBE_STATIC}", Static)
        ticket = self.tickets_by_path.get(path)
        # describe_output was computed once at scan / refresh time.
        output = ticket.describe_output if ticket else None
        describe_static.update(output or "No description available.")

    def on_data_table_row_highlighted(
        self, event: ObjectsDataTable.RowHighlighted
    ) -> None:
        try:
            row_data = event.data_table.get_row(event.row_key)
            self._show_description(row_data[0])
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
                ticket
                for ticket in self.original_data
                if any(search_query in str(cell).lower() for cell in ticket)
            ]

            # Add filtered rows back to the DataTable, keyed by path.
            self._populate_rows(data_table, filtered_data)
        except Exception:
            pass

    def on_key(self, event) -> None:
        if event.key == Keys.Enter:
            try:
                ticket = self._get_selected_ticket()
                self.exit(ticket)
            except Exception:
                pass

    def action_copy_path_clipboard(self) -> None:
        try:
            ticket = self._get_selected_ticket()
            copy_in_clipboard(ticket.path)
        except Exception:
            pass

        sys.exit(0)

    def action_refresh_tickets(self) -> None:
        # Rescan and re-describe everything, then refresh the cached description panel.
        tickets = self._scan_tickets()

        table = self.screen.query_one(ObjectsDataTable)
        table.clear()
        self._set_tickets(tickets)
        self._populate_rows(table, tickets)

    def action_convert_ticket(self) -> None:
        try:
            ticket = self._get_selected_ticket()
        except RowDoesNotExist:
            return
        except Exception:
            return

        output_path = kirbi_output_path(ticket.path)

        try:
            convert_ticket(
                ticket.path,
                output_path,
                self.config.kerberos.ticket_converter_command,
            )
            self.notify(f"Ticket converted to {output_path}", severity="information")
        except RuntimeError as e:
            self.notify(f"There was an error while converting: {e}", severity="error")
