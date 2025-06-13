from pykeepass import PyKeePass
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST


class Host:
    GROUP_NAME = "Hosts"
    EXEGOL_DB_ROLE_PROPERTY = "role"
    EXEGOL_DB_HOSTNAME_PROPERTY = "hostname"

    def __init__(self, id: str = "", ip: str = "", hostname: str = "", role: str = ""):
        self.id = id
        self.ip = ip
        self.hostname = hostname
        self.role = role

    def __iter__(self):
        return iter([self.id, self.ip, self.hostname, self.role])

    # Convert a Keepass entry into a Host object
    @staticmethod
    def host_from_entry(entry):
        return Host(
            entry.title if entry.title else "",
            entry.username if entry.username else "",
            entry.get_custom_property(Host.EXEGOL_DB_HOSTNAME_PROPERTY)
            if entry.get_custom_property(Host.EXEGOL_DB_HOSTNAME_PROPERTY)
            else "",
            entry.get_custom_property(Host.EXEGOL_DB_ROLE_PROPERTY)
            if entry.get_custom_property(Host.EXEGOL_DB_ROLE_PROPERTY)
            else "",
        )

    def __eq__(self, value):
        return (
            (self.id == value.id)
            and (self.ip == value.ip)
            and (self.hostname == value.hostname)
            and (self.role == value.role)
        )


def get_hosts(kp: PyKeePass, id: str = None) -> list[Host]:
    group = kp.find_groups(name=Host.GROUP_NAME, first=True)
    entries = kp.find_entries(title=id, recursive=True, group=group)

    return [Host.host_from_entry(entry) for entry in entries]


def get_new_host_id(kp: PyKeePass) -> str:
    hosts = get_hosts(kp)

    return str(int(hosts[-1].id) + 1) if hosts else "1"


def add_hosts(kp: PyKeePass, hosts: list[Host]):
    for host in hosts:
        add_host(kp, host)

    kp.save()


def add_host(kp: PyKeePass, host: Host):
    id = get_new_host_id(kp)
    host.id = id

    group = kp.find_groups(name=Host.GROUP_NAME, first=True)
    entry = kp.add_entry(group, id, host.ip, "")
    entry.set_custom_property(
        Host.EXEGOL_DB_HOSTNAME_PROPERTY, host.hostname, protect=True
    )
    entry.set_custom_property(Host.EXEGOL_DB_ROLE_PROPERTY, host.role, protect=True)


def delete_hosts(kp: PyKeePass, ids: list[str] = list()):
    for id in ids:
        delete_host(kp, id)

    kp.save()


def delete_host(kp: PyKeePass, id: str):
    group = kp.find_groups(name=Host.GROUP_NAME, first=True)
    entry = kp.find_entries(title=id, first=True, group=group)

    if entry:
        kp.delete_entry(entry)
    else:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)


def edit_hosts(kp: PyKeePass, hosts: list[Host]):
    for host in hosts:
        edit_host(kp, host)

    kp.save()


def edit_host(kp: PyKeePass, host: Host):
    group = kp.find_groups(name=Host.GROUP_NAME, first=True)
    entry = kp.find_entries(title=host.id, first=True, group=group)

    if entry:
        entry.title = host.id
        entry.username = host.ip
        entry.set_custom_property(
            Host.EXEGOL_DB_HOSTNAME_PROPERTY, host.hostname, protect=True
        )
        entry.set_custom_property(Host.EXEGOL_DB_ROLE_PROPERTY, host.role, protect=True)
    else:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)
