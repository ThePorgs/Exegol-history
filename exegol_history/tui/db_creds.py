from exegol_history.db_api.creds import add_credentials, delete_credentials, edit_credentials, get_credentials
from exegol_history.tui.objects_app import CopyAction, ObjectsApp
from exegol_history.tui.widgets.import_file import AssetsType


class DbCredsApp(ObjectsApp):
    ASSET_TYPE = AssetsType.Credentials
    NAME, PLURAL, ICON = "credential", "credentials", "🔑"
    COLUMNS = ("credential_id", "username", "password", "hash", "domain")
    COPY_ACTIONS = (
        CopyAction("username", "username", 1),
        CopyAction("password", "password", 2),
        CopyAction("hash", "hash", 3),
    )
    DOMAIN_COLUMN = 4

    def get_objects(self, object_id=None):
        return get_credentials(self.engine, credential_id=object_id)

    def add_objects(self, objects):
        add_credentials(self.engine, objects)

    def delete_objects(self, ids):
        delete_credentials(self.engine, ids)

    def edit_objects(self, objects):
        edit_credentials(self.engine, objects)