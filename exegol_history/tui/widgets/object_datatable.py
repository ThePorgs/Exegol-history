from textual.widgets import DataTable
from textual.widgets._data_table import RowDoesNotExist
from textual.widgets._data_table import CellType, ColumnKey, RowDoesNotExist, RowKey
from collections.abc import Iterable
from rich.text import Text

class _PlainCell(Text):
    """A cell displayed as literal text.

    DataTable renders str cells as Rich markup, so a value such as
    "Summer[/]2024" crashed the table and "[link=...]" or style tags were
    interpreted. The values shown here come from imported and synced data, so
    they are stored as Text, which DataTable always renders literally.
    """


def _to_cell(value: CellType) -> CellType:
    if isinstance(value, str):
        return _PlainCell(value)
    return value


def _from_cell(value: CellType) -> CellType:
    if isinstance(value, _PlainCell):
        return value.plain
    return value

class ObjectsDataTable(DataTable):
    def __init__(self):
        super().__init__()
        self.zebra_stripes = True
        self.cursor_type = "row"

    def add_row(self, *cells: CellType, **kwargs) -> RowKey:
        return super().add_row(*(_to_cell(cell) for cell in cells), **kwargs)

    def update_cell(
        self,
        row_key: RowKey | str,
        column_key: ColumnKey | str,
        value: CellType,
        **kwargs,
    ) -> None:
        super().update_cell(row_key, column_key, _to_cell(value), **kwargs)

    def get_row_values(self, row_key: RowKey | str) -> list[CellType]:
        return [_from_cell(cell) for cell in self.get_row(row_key)]

    def get_row_values_at(self, row_index: int) -> list[CellType]:
        return [_from_cell(cell) for cell in self.get_row_at(row_index)]

    def get_column_values_at(self, column_index: int) -> Iterable[CellType]:
        return (_from_cell(cell) for cell in self.get_column_at(column_index))


    def action_select_cursor(self) -> None:
        super().action_select_cursor()
        selected_row = self.cursor_coordinate.row
        try:
            row_data = self.get_row_values_at(selected_row)
            self.app.exit(row_data)
        except RowDoesNotExist:
            self.app.exit(None)
