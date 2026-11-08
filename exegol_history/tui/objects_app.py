from dataclasses import dataclass
from functools import partial

from sqlalchemy import Engine
from textual import work
from textual.app import SystemCommand
from textual.binding import Binding
from textual.keys import Keys
from textual.screen import Screen

from exegol_history.config.config import AppConfig
from exegol_history.db_api.exporting import export_objects
from exegol_history.tui.table_app import TableApp
from exegol_history.tui.widgets.import_file import AssetsType

FUNCTION_KEYS = [Keys.F1, Keys.F2, Keys.F3, Keys.F4, Keys.F5, Keys.F6, Keys.F7, Keys.F8]


@dataclass(frozen=True)
class CopyAction:
    field: str
    label: str
    column: int


class ObjectsApp(TableApp):
    """Table of objects (credentials, hosts) with search, copy, add, delete,
    edit and export. Subclasses only describe what differs."""

    ASSET_TYPE: AssetsType
    NAME = ""
    PLURAL = ""
    COPY_ACTIONS: tuple[CopyAction, ...] = ()
    DOMAIN_COLUMN: int | None = None  # column feeding the domain suggester

    def __init_subclass__(cls, **kwargs):
        # BINDINGS must be set before Textual's __init_subclass__ merges them.
        if cls.NAME:
            cls.BINDINGS = cls._build_bindings()
        super().__init_subclass__(**kwargs)

    @classmethod
    def _build_bindings(cls) -> list[Binding]:
        icons = cls.config.theme
        # (action, footer text, binding id used by the keymap, tooltip)
        actions = [
            (
                f"copy_column({c.column})",
                f"{icons.clipboard_icon} {c.label}",
                f"copy_{c.field}_clipboard",
                f"Copy the {c.label} to the clipboard",
            )
            for c in cls.COPY_ACTIONS
        ] + [
            (
                "add_object",
                f"{icons.add_icon} {cls.NAME}",
                f"add_{cls.NAME}",
                f"Add a new {cls.NAME}",
            ),
            (
                "delete_object",
                f"{icons.delete_icon} {cls.NAME}",
                f"delete_{cls.NAME}",
                f"Delete the selected {cls.NAME} or multiple {cls.PLURAL}",
            ),
            (
                "edit_object",
                f"{icons.edit_icon} {cls.NAME}",
                f"edit_{cls.NAME}",
                f"Edit the selected {cls.NAME}",
            ),
            (
                "export_objects",
                f"{icons.export_icon} {cls.NAME}",
                f"export_{cls.NAME}",
                f"Export {cls.PLURAL}",
            ),
        ]
        return [
            Binding(key, action, description, id=binding_id, tooltip=tooltip)
            for key, (action, description, binding_id, tooltip) in zip(
                FUNCTION_KEYS, actions
            )
        ] + [Binding(Keys.ControlC, "quit", "Quit", show=False, priority=True)]

    def get_objects(self, object_id=None) -> list: ...
    def add_objects(self, objects: list) -> None: ...
    def delete_objects(self, ids: list) -> None: ...
    def edit_objects(self, objects: list) -> None: ...

    def __init__(
        self,
        config: AppConfig,
        engine: Engine,
        show_add_screen: bool = False,
        background_sync: bool = False,
    ):
        self.CSS_PATH = "css/general.tcss"
        super().__init__(config, engine)
        self.show_add_screen = show_add_screen
        self.background_sync = background_sync

    def update_table(self) -> None:
        self.set_rows(self.get_objects())

    def selected_object(self, row: list):
        return self.get_objects(row[0])[0]

    def domains(self) -> dict:
        if self.DOMAIN_COLUMN is None:
            return {}
        return {
            "domains": set(
                filter(None, self.table.get_column_values_at(self.DOMAIN_COLUMN))
            )
        }

    def load_data(self) -> None:
        # Called by TableApp.on_mount: don't define on_mount here, Textual
        # would run both and add every column twice.
        self.update_table()
        if self.show_add_screen:
            self.action_add_object()
        if self.background_sync:
            self.sync_connectors()

    @work(thread=True, exclusive=True, group="sync", exit_on_error=False)
    def sync_connectors(self) -> None:
        from exegol_history.db_api.sync import sync_objects

        try:
            sync_objects(self.engine, self.config, True, True)
        except Exception:
            return
        self.call_from_thread(self.update_table)

    def action_add_object(self) -> None:
        from exegol_history.tui.screens.add_object import AddObjectScreen

        def on_added(objects: list) -> None:
            self.add_objects(objects)
            self.update_table()
            if self.show_add_screen:
                self.exit()

        self.push_screen(AddObjectScreen(self.ASSET_TYPE, **self.domains()), on_added)

    def action_delete_object(self) -> None:
        from exegol_history.tui.screens.delete_object import DeleteObjectScreen

        def on_confirmed(ids: list) -> None:
            for object_id in ids:
                try:
                    self.delete_objects([object_id])
                except RuntimeError:
                    pass
            self.update_table()

        if row := self.selected_row():
            self.push_screen(DeleteObjectScreen([row[0]]), on_confirmed)

    def action_edit_object(self) -> None:
        from exegol_history.tui.screens.edit_object import EditObjectScreen

        def on_edited(obj) -> None:
            try:
                self.edit_objects([obj])
            except RuntimeError as e:
                self.notify(
                    f"There was an error while editing: {e}",
                    severity="error",
                    markup=False,
                )
            self.update_table()

        if row := self.selected_row():
            obj = self.get_objects(row[0])[0]
            self.push_screen(
                EditObjectScreen(self.ASSET_TYPE, obj, **self.domains()), on_edited
            )

    def action_export_objects(self) -> None:
        from exegol_history.tui.screens.export_object import ExportObjectScreen

        def on_chosen(result: tuple | None) -> None:
            if not result or not result[1]:
                return
            file_format, export_path = result
            try:
                with open(export_path, "w", newline="") as f:
                    f.write(export_objects(file_format, self.get_objects()))
                self.notify(
                    f"{self.PLURAL.capitalize()} successfully exported !",
                    severity="information",
                )
            except Exception as e:
                self.notify(
                    f"There was an error while exporting: {e}",
                    severity="error",
                    markup=False,
                )

        self.push_screen(ExportObjectScreen(self.ASSET_TYPE), on_chosen)

    def get_system_commands(self, screen: Screen):
        for c in self.COPY_ACTIONS:
            yield SystemCommand(
                f"Copy {c.label}",
                f"Copy the {c.label} to the clipboard",
                partial(self.action_copy_column, c.column),
            )
        yield SystemCommand(
            f"Add {self.NAME}", f"Add a new {self.NAME}", self.action_add_object
        )
        yield SystemCommand(
            f"Delete {self.NAME}",
            f"Delete the selected {self.NAME}",
            self.action_delete_object,
        )
        yield SystemCommand(
            f"Edit {self.NAME}",
            f"Edit the selected {self.NAME}",
            self.action_edit_object,
        )
        yield SystemCommand(
            f"Export {self.PLURAL}", f"Export {self.PLURAL}", self.action_export_objects
        )
