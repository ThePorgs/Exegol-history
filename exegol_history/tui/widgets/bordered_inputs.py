from textual.widgets import Input


class BorderedInput(Input):
    def __init__(self, border_title, **kwargs):
        super().__init__(**kwargs)
        self.border_title = border_title
