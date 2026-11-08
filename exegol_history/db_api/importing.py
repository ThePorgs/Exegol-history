import csv
import io
import json
from xml.etree import ElementTree

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.file_types import (
    CredsImportFileType,
    HostsImportFileType,
)
from exegol_history.db_api.hosts import Host

CREDS_DEFAULTS = {
    "username": "",
    "password": "",
    "hash": "",
    "domain": "",
    "sync_key": "",
}
HOSTS_DEFAULTS = {"ip": "", "hostname": "", "role": ""}
PYPYKATZ_SECRETS = {
    "msv_creds": ("NThash", "hash"),
    "wdigest_creds": ("password", "password"),
}
NMAP_HOSTNAME_PRIORITY = ("user", "PTR")


def import_objects(
    file_type: CredsImportFileType | HostsImportFileType,
    file_raw: bytes,
    kdbx_password: str = None,
    keyfile_path: str = None,
) -> list[Credential | Host]:
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
        case HostsImportFileType.NMAP_XML:
            objects = import_hosts_nmap_xml(file_raw)
        case _:
            raise NotImplementedError(
                f"Type {file_type} is not implemented yet for import"
            )

    if isinstance(file_type, CredsImportFileType):
        defaults, allowed = CREDS_DEFAULTS, {*CREDS_DEFAULTS, "credential_id"}
    else:
        defaults, allowed = HOSTS_DEFAULTS, {*HOSTS_DEFAULTS, "host_id"}

    rows = [{**defaults, **row} for row in objects]
    if unknown := {key for row in rows for key in row} - allowed:
        raise ValueError(f"Unknown column(s): {', '.join(sorted(unknown))}")

    return rows


def import_objects_csv(file_raw: bytes):
    file_raw = io.StringIO(file_raw.decode("utf-8"))
    dialect = csv.Sniffer().sniff(file_raw.readline())
    file_raw.seek(0)

    return csv.DictReader(file_raw, delimiter=dialect.delimiter, restval="")


def import_creds_pypykatz_json(file_raw: bytes) -> list[dict]:
    credentials_json = json.loads(file_raw)
    logon_sessions = next(iter(credentials_json.values()))["logon_sessions"]
    parsed_credentials = {}

    for session in logon_sessions.values():
        for section, (secret_field, field) in PYPYKATZ_SECRETS.items():
            for entry in session.get(section) or []:
                username, domain = entry["username"], entry["domainname"]
                credential = parsed_credentials.setdefault(
                    (username, domain),
                    {
                        "username": username,
                        "password": "",
                        "hash": "",
                        "domain": domain,
                    },
                )
                credential[field] = entry[secret_field] or ""

    return list(parsed_credentials.values())


def import_creds_secretsdump(file_raw: bytes) -> list[dict]:
    rows = csv.reader(io.StringIO(file_raw.decode("utf-8")), delimiter=":")
    return [Credential.dict(username=row[0], hash=row[3]) for row in rows]


def import_creds_kdbx(
    file_raw, kdbx_password: str = None, keyfile_path: str = None
) -> list[dict]:
    from pykeepass import PyKeePass

    kp = PyKeePass(io.BytesIO(file_raw), password=kdbx_password, keyfile=keyfile_path)
    return [
        Credential.dict(username=e.username, password=e.password) for e in kp.entries
    ]


def import_hosts_nmap_xml(file_raw: bytes) -> list[dict]:
    """Hosts from an Nmap XML report (nmap -oX): one per IP address of every
    host that is up, with its hostname when Nmap found one.

    ElementTree never resolves external entities and the bundled expat (2.4.1+)
    rejects entity expansion attacks, so untrusted reports are safe to parse.
    """
    try:
        report = ElementTree.fromstring(file_raw)
    except ElementTree.ParseError as e:
        raise ValueError(f"Invalid Nmap XML report: {e}") from e

    if report.tag != "nmaprun":
        raise ValueError(
            "Invalid Nmap XML report: the root element should be <nmaprun>"
        )

    hosts = {}
    for host in report.findall("host"):
        status = host.find("status")
        if status is not None and status.get("state") != "up":
            continue

        names = {
            name.get("type"): name.get("name", "")
            for name in host.findall("hostnames/hostname")
        }
        hostname = next(
            (names[t] for t in NMAP_HOSTNAME_PRIORITY if names.get(t)),
            next(iter(names.values()), ""),
        )

        for address in host.findall("address"):
            if address.get("addrtype") in ("ipv4", "ipv6") and address.get("addr"):
                ip = address.get("addr")
                # (ip, hostname) is unique in the database: keep one row each
                hosts[(ip, hostname.lower())] = Host.dict(ip=ip, hostname=hostname)

    return list(hosts.values())
