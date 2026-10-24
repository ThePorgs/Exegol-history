from textual.binding import Binding
from textual.widgets import Input

from exegol_history.tui.widgets.object_datatable import ObjectsDataTable


class SearchInput(Input):
    """Search bar that forwards vertical navigation keys to the table."""

    BINDINGS = [
        Binding("up", "table('cursor_up')", show=False),
        Binding("down", "table('cursor_down')", show=False),
        Binding("pageup", "table('page_up')", show=False),
        Binding("pagedown", "table('page_down')", show=False),
    ]

    def action_table(self, action: str) -> None:
        table = self.screen.query_one(ObjectsDataTable)
        getattr(table, f"action_{action}")()