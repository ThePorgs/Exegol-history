from textual import on
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import (
    Select,
    Button,
    Input,
    TabbedContent,
    TabPane,
    Label,
    TextArea,
)
from textual.containers import Vertical, Horizontal
from textual.validation import Length

from exegol_history.db_api.parsing import parse_creds, CredsFileType
from exegol_history.tui.common.open_file import OpenFileScreen

"""
This screen is used to add a credential
"""


class AddCredentialScreen(ModalScreen):
    CSS_PATH = "../css/add_object.tcss"

    selected_format = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            with TabbedContent():
                with TabPane("Add a single credential", id="single"):
                    yield Input(
                        placeholder="Username",
                        id="username",
                        validators=[Length(minimum=1)],
                    )
                    yield Input(placeholder="Password", id="password")
                    yield Input(placeholder="Hash", id="hash")
                    yield Input(placeholder="Domain", id="domain")
                    with Horizontal(id="add_confirm"):
                        yield Button(" Confirm", variant="success", id="confirm_add")
                        yield Button(" Cancel", variant="error", id="cancel")

                with TabPane("Import from file", id="import_tab"):
                    yield Label("Either import a file, or directly paste:")
                    yield TextArea.code_editor("", id="file_textarea")
                    with Horizontal(id="horizontal_error"):
                        # Reference: https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class
                        options = [
                            (cred_type.name, cred_type.value)
                            for cred_type in CredsFileType
                        ]
                        yield Select(
                            options,
                            prompt="Select an import format",
                            id="file_type_select",
                        )
                    with Horizontal(id="add_confirm"):
                        yield Button(
                            " Confirm", variant="success", id="confirm_import"
                        )
                        yield Button(" Cancel", variant="error", id="cancel")
                        yield Button(" Import", variant="primary", id="import_file")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.selected_format = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "import_file":

            def check_import(path: str):
                file_content = ""
                with open(path, "r") as f:
                    file_content = f.read()

                self.query_one(TextArea).text = file_content

            self.app.push_screen(OpenFileScreen(), check_import)

        if event.button.id == "confirm_import":
            try:
                parsed_creds = parse_creds(
                    self.selected_format, self.query_one(TextArea).text
                )
                if not parsed_creds:
                    self.notify("Please choose an import format", severity="warning")
                else:
                    self.dismiss(parsed_creds)
            except Exception as e:
                self.notify(f"{e}", title="Error parsing the content", severity="error")
                pass
        elif event.button.id == "confirm_add":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            hash = self.query_one("#hash", Input).value
            domain = self.query_one("#domain", Input).value

            if username:
                self.dismiss([(username, password, hash, domain)])

        if event.button.id == "cancel":
            self.app.pop_screen()
