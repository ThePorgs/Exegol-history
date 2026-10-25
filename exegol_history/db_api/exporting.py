import csv
import io
import json
from typing import Any

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.db_api.importing import CredsImportFileType, HostsImportFileType

CREDENTIAL_PROPERTY_NAME_ID = "credential_id"
HOST_PROPERTY_NAME_ID = "host_id"


def export_objects(
    format: CredsImportFileType | HostsImportFileType,
    objects: list[Any],
    delimiter: str = None,
) -> str:
    match format:
        case CredsImportFileType.CSV:
            export_output = export_objects_csv(objects, delimiter, Credential)
        case HostsImportFileType.CSV:
            export_output = export_objects_csv(objects, delimiter, Host)
        case CredsImportFileType.JSON | HostsImportFileType.JSON:
            export_output = export_objects_json(objects)
        case _:
            raise NotImplementedError(
                f"Type {format} is not implemented yet for export"
            )

    return export_output


def export_objects_json(objects: list[Any]):
    results = []

    for object in objects:
        dict = object.as_dict()
        dict.pop(CREDENTIAL_PROPERTY_NAME_ID, None)
        dict.pop(HOST_PROPERTY_NAME_ID, None)
        results.append(dict)

    return json.dumps(results)


def export_objects_csv(
    objects: list[Credential | Host],
    delimiter: str,
    obj_type: type[Credential | Host],
):
    csv_string = io.StringIO()
    csv_writer = csv.writer(
        csv_string,
        delimiter=delimiter if delimiter else ",",
    )
    csv_writer.writerow([column.name for column in obj_type.__mapper__.columns][1:])

    for o in objects:
        csv_writer.writerow(
            [getattr(o, column.name) for column in obj_type.__mapper__.columns][1:]
        )

    return csv_string.getvalue()
