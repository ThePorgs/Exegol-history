from textual.widgets import DataTable
from textual.widgets._data_table import RowDoesNotExist


class ObjectsDataTable(DataTable):
    def __init__(self):
        super().__init__()

    def action_select_cursor(self) -> None:
        super().action_select_cursor()
        selected_row = self.cursor_coordinate.row
        try:
            row_data = self.get_row_at(selected_row)
            self.app.exit(row_data)
        except RowDoesNotExist:
            self.app.exit(None)
