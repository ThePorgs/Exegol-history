from pykeepass import PyKeePass

EXEGOL_DB_ROLE_PROPERTY = "role"
EXEGOL_DB_HOSTNAME_PROPERTY = "hostname"

GROUP_NAME_HOSTS = "Hosts"


def get_hosts(kp: PyKeePass, searched_ip: str = "") -> [(str, str, str)]:
    array = []
    group = kp.find_groups(name=GROUP_NAME_HOSTS, first=True)

    for entry in group.entries:
        ip = entry.title
        hostname = entry.get_custom_property(EXEGOL_DB_HOSTNAME_PROPERTY)
        role = entry.get_custom_property(EXEGOL_DB_ROLE_PROPERTY)

        if ip == searched_ip:
            array.append((ip, hostname, role))
            return array
        elif not searched_ip:
            array.append((ip, hostname, role))

    return array


def add_host(kp: PyKeePass, host_ip: str, hostname: str = "", role: str = ""):
    if not host_ip:
        raise ValueError("IP cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_HOSTS, first=True)

    try:
        entry = kp.add_entry(group, host_ip, host_ip, "")
        entry.set_custom_property(EXEGOL_DB_HOSTNAME_PROPERTY, hostname, protect=True)
        entry.set_custom_property(EXEGOL_DB_ROLE_PROPERTY, role, protect=True)
    except Exception:
        entry = kp.find_entries(title=host_ip, first=True, group=group)
        edit_host(kp, entry.title, host_ip, hostname, role)

    kp.save()


def delete_host(kp: PyKeePass, host_ip: str):
    group = kp.find_groups(name=GROUP_NAME_HOSTS, first=True)
    entry = kp.find_entries(title=host_ip, first=True, group=group)

    if entry:
        kp.delete_entry(entry)
        kp.save()
    else:
        raise RuntimeError("The provided host_ip does not exist")


def edit_host(kp: PyKeePass, old_ip: str, ip: str, hostname: str = "", role: str = ""):
    if not ip:
        raise ValueError("IP cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_HOSTS, first=True)

    try:
        entry = kp.find_entries(title=old_ip, first=True, group=group)
        entry.title = ip

        entry.set_custom_property(EXEGOL_DB_HOSTNAME_PROPERTY, hostname, protect=True)
        entry.set_custom_property(EXEGOL_DB_ROLE_PROPERTY, role, protect=True)
    except Exception:
        pass

    kp.save()
