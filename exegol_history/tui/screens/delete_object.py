from textual.screen import ModalScreen
from textual.app import ComposeResult
from exegol_history.db_api.utils import parse_ids
from exegol_history.tui.widgets.action_buttons import ActionButtons
from textual.widgets import Static, Input, Button, Tabs
from textual.widgets import TabbedContent, TabPane
from textual.containers import Container

"""
This screen is used to delete the selected host
"""
ID_IDS_INPUT = "ids_input"

ID_CONFIRM_BUTTON = "confirm_button"
ID_CONFIRM_RANGE_BUTTON = "confirm_range_button"
ID_CANCEL_BUTTON = "cancel_button"

ID_SINGLE_TAB = "single_tab"
ID_RANGE_TAB = "range_tab"


class DeleteObjectScreen(ModalScreen):
    def __init__(self, ids: list[int]):
        super().__init__()
        self.ids = ids
        self.selected_tab = ""

    def compose(self) -> ComposeResult:
        container = Container()
        container.border_title = "🗑️ Deleting objects"

        with container:
            with TabbedContent():
                with TabPane("Selected object", id=ID_SINGLE_TAB):
                    yield Static(
                        "Are you sure you want to remove that object?",
                        id="question",
                    )
                    yield ActionButtons()
                with TabPane("Multiple objects", id=ID_RANGE_TAB):
                    yield Static(
                        "Delete multiple objects, using comma to separate value, and '-' to include ranges.",
                        id="question",
                    )
                    yield Input(placeholder="1,2,6-8", id=ID_IDS_INPUT)
                    yield ActionButtons(confirm_button_id=ID_CONFIRM_RANGE_BUTTON)

        # tmp = DeleteObjects(ids=self.ids)
        # tmp.border_title = "sfdadasdsa"
        # yield tmp

    def on_tabbed_content_tab_activated(self, event: Tabs.TabActivated):
        self.selected_tab = event.tab.id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.selected_tab == f"--content-tab-{ID_RANGE_TAB}":
            ids = self.screen.query_one(f"#{ID_IDS_INPUT}", Input).value
            self.ids = parse_ids(ids)

        if event.button.id in (ID_CONFIRM_BUTTON, ID_CONFIRM_RANGE_BUTTON):
            self.screen.dismiss(self.ids)
