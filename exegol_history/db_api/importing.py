from enum import Enum
from typing import Any
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from pykeepass import PyKeePass
import json
import io
import csv


class CredsImportFileType(Enum):
    CSV = 1
    JSON = 2
    KDBX = 3
    PYPYKATZ_JSON = 4
    SECRETSDUMP = 5


class HostsImportFileType(Enum):
    CSV = 1
    JSON = 2


def import_objects(
    file_type: CredsImportFileType | HostsImportFileType,
    file_raw: bytes,
    kdbx_password: str = None,
    keyfile_path: str = None,
) -> list[Credential | Host]:
    result = list()

    match file_type:
        case CredsImportFileType.PYPYKATZ_JSON:
            objects = import_creds_pypykatz_json(file_raw)
        case CredsImportFileType.SECRETSDUMP:
            objects = import_creds_secretsdump(file_raw)
        case CredsImportFileType.KDBX:
            objects = import_creds_kdbx(file_raw, kdbx_password, keyfile_path)
        case CredsImportFileType.CSV | HostsImportFileType.CSV:
            objects = import_objects_csv(file_raw)
        case CredsImportFileType.JSON | HostsImportFileType.JSON:
            objects = json.loads(file_raw)

    for object in objects:
        # Reference: https://stackoverflow.com/questions/2544710/how-i-can-get-rid-of-none-values-in-dictionary, answer by John La Rooy
        # Remove 'None' value
        object = {k: v for k, v in object.items() if v is not None}

        try:
            object_to_add = (
                Credential(**object)
                if type(file_type) is CredsImportFileType
                else Host(**object)
            )
        except TypeError:
            raise TypeError(
                "Error while importing, is the file in the correct format ?"
            )

        result.append(object_to_add)

    return result


def import_objects_csv(file_raw: bytes):
    file_raw = io.StringIO(file_raw.decode("utf-8"))
    dialect = csv.Sniffer().sniff(file_raw.readline())
    file_raw.seek(0)
    return csv.DictReader(file_raw, delimiter=dialect.delimiter)


def import_creds_pypykatz_json(file_raw: bytes) -> dict[Any]:
    parsed_credentials = dict()
    credentials_json = json.load(io.BytesIO(file_raw))
    logon_sessions = credentials_json[[*credentials_json][0]]["logon_sessions"]

    for key, sessions in logon_sessions.items():
        if sessions.get("msv_creds"):
            for msv_credential in sessions.get("msv_creds"):
                username = msv_credential["username"]
                nt_hash = msv_credential["NThash"]
                domain = msv_credential["domainname"]
                dict_key = f"{username}\\{domain}"

                if dict_key not in parsed_credentials:
                    parsed_credentials[dict_key] = Credential(
                        username=username, hash=nt_hash, domain=domain
                    )
                else:
                    parsed_credentials[dict_key].hash = nt_hash if nt_hash else ""

        if sessions.get("wdigest_creds"):
            for wdigest_credential in sessions.get("wdigest_creds"):
                username = wdigest_credential["username"]
                password = wdigest_credential["password"]
                domain = wdigest_credential["domainname"]
                dict_key = f"{username}\\{domain}"

                if dict_key not in parsed_credentials:
                    parsed_credentials[dict_key] = Credential(
                        username=username, password=password, domain=domain
                    )
                else:
                    parsed_credentials[dict_key].password = password if password else ""

    return [credential.__dict__ for _key, credential in parsed_credentials.items()]


def import_creds_secretsdump(file_raw: bytes) -> list[Credential]:
    parsed_credentials = []
    credentials = csv.reader(
        io.StringIO(file_raw.decode("utf-8")),
        delimiter=":",
    )

    for row in credentials:
        credential = Credential(username=row[0], hash=row[3])
        parsed_credentials.append(credential.__dict__)

    return parsed_credentials


def import_creds_kdbx(
    file_raw, kdbx_password: str = None, keyfile_path: str = None
) -> list[Credential]:
    parsed_credentials = list()
    kp = PyKeePass(io.BytesIO(file_raw), password=kdbx_password, keyfile=keyfile_path)

    for entry in kp.entries:
        credential = Credential(username=entry.username, password=entry.password)
        parsed_credentials.append(credential.__dict__)

    return parsed_credentials
