from textual.widgets import DataTable


class ObjectsDataTable(DataTable):
    def __init__(self):
        super().__init__()

    def action_select_cursor(self) -> None:
        super().action_select_cursor()
        selected_row = self.cursor_coordinate.row
        row_data = self.get_row_at(selected_row)
        self.app.exit(row_data)
