import io
import json
import csv
from typing import Any, Type, Union
from enum import Enum

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.db_api.importing import CredsImportFileType, HostsImportFileType

PROPERTY_NAME_ID = "id"


class CredsExportFileType(Enum):
    CSV = 1
    JSON = 2


class HostsExportFileType(Enum):
    CSV = 1
    JSON = 2


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
            raise NotImplementedError(f"Type {format} is not implemented yet for export")

    return export_output


def export_objects_json(objects: list[Any]):
    results = list()

    for object in objects:
        dict = object.__dict__
        dict.pop(PROPERTY_NAME_ID, None)
        results.append(dict)

    return json.dumps(results)


def export_objects_csv(objects: list[Union[Credential, Host]], delimiter: str, obj_type: Type[Union[Credential, Host]]):

    csv_string = io.StringIO()
    csv_writer = csv.DictWriter(
        csv_string,
        fieldnames=obj_type.HEADERS,
        delimiter=delimiter if delimiter else ",",
    )
    csv_writer.writeheader()

    for o in objects:
        obj_dict = o.__dict__
        obj_dict.pop(PROPERTY_NAME_ID, None)
        csv_writer.writerow(obj_dict)

    return csv_string.getvalue()
