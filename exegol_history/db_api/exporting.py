import io
import json
import csv
from typing import Any
from enum import Enum
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
        case CredsImportFileType.CSV | HostsImportFileType.CSV:
            export_output = export_objects_csv(objects, delimiter)
        case CredsImportFileType.JSON | HostsImportFileType.JSON:
            export_output = export_objects_json(objects)

    return export_output


def export_objects_json(objects: list[Any]):
    results = list()

    for object in objects:
        dict = object.__dict__
        dict.pop(PROPERTY_NAME_ID, None)
        results.append(dict)

    return json.dumps(results)


def export_objects_csv(objects: list[Any], delimiter: str = None):
    if not objects:
        return

    csv_string = io.StringIO(newline="")
    csv_writer = csv.DictWriter(
        csv_string,
        fieldnames=list(objects[0].__dict__.keys())[1:],
        delimiter=delimiter if delimiter else ",",
    )
    csv_writer.writeheader()

    for object in objects:
        dict = object.__dict__
        dict.pop(PROPERTY_NAME_ID, None)
        csv_writer.writerow(dict)

    return csv_string.getvalue()
