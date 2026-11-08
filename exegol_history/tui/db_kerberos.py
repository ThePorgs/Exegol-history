from textual import work
from textual.app import ComposeResult, SystemCommand
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.keys import Keys
from textual.screen import Screen
from textual.widgets import Static

from exegol_history.config.config import AppConfig
from exegol_history.db_api.kerberos import (
    Ticket,
    convert_ticket,
    describe_and_enrich_tickets,
    kirbi_output_path,
    scan_ccache_tickets,
)
from exegol_history.tui.objects_app import TableApp
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


class DbKerberosApp(TableApp):
    COLUMNS = ("path", "username", "domain")
    BINDINGS = [
        Binding(
            Keys.F1,
            "copy_column(0)",
            f"{TableApp.config.theme.clipboard_icon} path",
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
        super().__init__(config, engine)
        self.tickets_by_path: dict[str, Ticket] = {}

    def compose_main(self) -> ComposeResult:
        with Horizontal(id=ID_MAIN_HORIZONTAL):
            yield ObjectsDataTable()
            with VerticalScroll(id=ID_DESCRIBE_PANEL):
                yield Static(
                    "Select a ticket to display its description.",
                    id=ID_DESCRIBE_STATIC,
                    markup=False,
                )

    def load_data(self) -> None:
        # Scanning and running describeTicket.py (one process per ticket) is
        # slow: do it in a thread so the TUI shows up immediately.
        self.load_tickets()

    def add_table_rows(self, rows) -> None:
        for row in rows:
            self.table.add_row(*row, key=row[0])

    @work(thread=True, exclusive=True, group="scan")
    def load_tickets(self) -> None:
        self.call_from_thread(setattr, self.table, "loading", True)
        tickets = scan_ccache_tickets(
            self.config.kerberos.search_paths, self.config.kerberos.search_depth
        )
        describe_and_enrich_tickets(
            tickets, self.config.kerberos.describe_ticket_command
        )
        self.call_from_thread(self._show_tickets, tickets)

    def _show_tickets(self, tickets: list[Ticket]) -> None:
        self.table.loading = False
        self.tickets_by_path = {ticket.path: ticket for ticket in tickets}
        self.set_rows(tickets)

    def selected_object(self, row: list) -> Ticket:
        return Ticket(*row)

    def on_data_table_row_highlighted(
        self, event: ObjectsDataTable.RowHighlighted
    ) -> None:
        ticket = self.tickets_by_path.get(event.row_key.value)
        output = ticket.describe_output if ticket else None
        self.query_one(f"#{ID_DESCRIBE_STATIC}", Static).update(
            output or "No description available."
        )

    def action_refresh_tickets(self) -> None:
        self.load_tickets()

    def action_convert_ticket(self) -> None:
        if not (row := self.selected_row()):
            return

        output_path = kirbi_output_path(row[0])
        try:
            convert_ticket(
                row[0], output_path, self.config.kerberos.ticket_converter_command
            )
            self.notify(
                f"Ticket converted to {output_path}",
                severity="information",
                markup=False,
            )
        except RuntimeError as e:
            self.notify(
                f"There was an error while converting: {e}",
                severity="error",
                markup=False,
            )

    def get_system_commands(self, screen: Screen):
        yield SystemCommand(
            "Copy path", TOOLTIP_COPY_PATH, lambda: self.action_copy_column(0)
        )
        yield SystemCommand(
            "Convert ticket", TOOLTIP_CONVERT_TICKET, self.action_convert_ticket
        )
        yield SystemCommand(
            "Refresh tickets", TOOLTIP_REFRESH_TICKETS, self.action_refresh_tickets
        )
