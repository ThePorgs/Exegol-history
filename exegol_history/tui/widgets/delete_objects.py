from textual.app import ComposeResult
from textual.widgets import Button, Input, TabbedContent, TabPane, Tabs, Static
from textual.containers import Container
from exegol_history.db_api.utils import parse_ids
from exegol_history.tui.widgets.action_buttons import ActionButtons

ID_IDS_INPUT = "ids_input"

ID_CONFIRM_BUTTON = "confirm_button"
ID_CONFIRM_RANGE_BUTTON = "confirm_range_button"
ID_CANCEL_BUTTON = "cancel_button"

ID_SINGLE_TAB = "single_tab"
ID_RANGE_TAB = "range_tab"


class DeleteObjects(Container):
    def __init__(self, ids: list[int], id: str = None):
        super().__init__(id=id)
        self.selected_tab = ""
        self.ids = ids

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Delete the selected object", id=ID_SINGLE_TAB):
                yield Static(
                    "Are you sure you want to remove that object?",
                    id="question",
                )
                yield ActionButtons()

            with TabPane("Delete multiple objects", id=ID_RANGE_TAB):
                yield Static(
                    "Delete multiple objects, using comma to separate value, and '-' to include ranges.",
                    id="question",
                )
                yield Input(placeholder="1,2,6-8", id=ID_IDS_INPUT)
                yield ActionButtons(confirm_button_id=ID_CONFIRM_RANGE_BUTTON)

    def on_tabbed_content_tab_activated(self, event: Tabs.TabActivated):
        self.selected_tab = event.tab.id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.selected_tab == f"--content-tab-{ID_RANGE_TAB}":
            ids = self.query_one(f"#{ID_IDS_INPUT}", Input).value
            self.ids = parse_ids(ids)

        if event.button.id in (ID_CONFIRM_BUTTON, ID_CONFIRM_RANGE_BUTTON):
            self.screen.dismiss(self.ids)
