import csv
import io
import json

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.db_api.importing import CredsImportFileType, HostsImportFileType

CREDENTIAL_PROPERTY_NAME_ID = "credential_id"
CREDENTIAL_PROPERTY_NAME_SYNC_KEY = "sync_key"
HOST_PROPERTY_NAME_ID = "host_id"
EXCLUDED_COLUMNS = {"credential_id", "host_id", "sync_key"}


def exported_columns(model) -> list[str]:
    return [c.name for c in model.__table__.columns if c.name not in EXCLUDED_COLUMNS]


def export_objects(format, objects, delimiter: str = None) -> str:
    model = Credential if isinstance(format, CredsImportFileType) else Host
    columns = exported_columns(model)
    rows = [{c: getattr(o, c) for c in columns} for o in objects]

    match format:
        case CredsImportFileType.JSON | HostsImportFileType.JSON:
            return json.dumps(rows)
        case CredsImportFileType.CSV | HostsImportFileType.CSV:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns, delimiter=delimiter or ",")
            writer.writeheader()
            writer.writerows(rows)
            return output.getvalue()
        case _:
            raise NotImplementedError(f"Type {format} is not implemented yet for export")