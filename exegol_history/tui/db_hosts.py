from exegol_history.db_api.hosts import add_hosts, delete_hosts, edit_hosts, get_hosts
from exegol_history.tui.objects_app import CopyAction, ObjectsApp
from exegol_history.tui.widgets.import_file import AssetsType


class DbHostsApp(ObjectsApp):
    ASSET_TYPE = AssetsType.Hosts
    NAME, PLURAL, ICON = "host", "hosts", "🔑"
    COLUMNS = ("host_id", "ip", "hostname", "role")
    COPY_ACTIONS = (CopyAction("ip", "IP", 1), CopyAction("hostname", "hostname", 2))

    def get_objects(self, object_id=None):
        return get_hosts(self.engine, host_id=object_id)

    def add_objects(self, objects):
        add_hosts(self.engine, objects)

    def delete_objects(self, ids):
        delete_hosts(self.engine, ids)

    def edit_objects(self, objects):
        edit_hosts(self.engine, objects)