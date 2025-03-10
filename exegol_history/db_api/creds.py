from pykeepass import PyKeePass

GROUP_NAME_CREDENTIALS = "Credentials"
EXEGOL_DB_HASH_PROPERTY = "hash"
EXEGOL_DB_DOMAIN_PROPERTY = "domain"


def add_credential(
    kp: PyKeePass, username: str, password: str = "", hash: str = "", domain: str = ""
):
    if not username:
        raise ValueError("Username cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)

    try:
        entry = kp.add_entry(group, username, username, password)
        entry.set_custom_property(EXEGOL_DB_HASH_PROPERTY, hash, protect=True)
        entry.set_custom_property(EXEGOL_DB_DOMAIN_PROPERTY, domain, protect=True)
    except Exception:
        entry = kp.find_entries(title=username, first=True, group=group)
        edit_credential(kp, entry.title, username, password, hash, domain)

    kp.save()


def get_credentials(
    kp: PyKeePass, searched_username: str = "", redacted: bool = "false"
) -> [(str, str, str, str)]:
    array = []
    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)

    for entry in group.entries:
        username = entry.username
        password = entry.password
        hash = entry.get_custom_property(EXEGOL_DB_HASH_PROPERTY)
        domain = entry.get_custom_property(EXEGOL_DB_DOMAIN_PROPERTY)

        if redacted:
            password = "**********"
            hash = "**********"

        if not username:
            username = ""

        if not password:
            password = ""

        if not hash:
            hash = ""

        if not domain:
            domain = ""

        if searched_username == username:
            array.append((username, password, hash, domain))
            return array
        elif not searched_username:
            array.append((username, password, hash, domain))

    return array


def delete_credential(kp: PyKeePass, username: str):
    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)
    entry = kp.find_entries(title=username, first=True, group=group)

    if entry:
        kp.delete_entry(entry)
        kp.save()
    else:
        raise RuntimeError("The provided username does not exist")


def edit_credential(
    kp: PyKeePass,
    old_username: str,
    username: str,
    password: str = "",
    hash: str = "",
    domain: str = "",
):
    if not username:
        raise ValueError("Username cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)

    try:
        entry = kp.find_entries(title=old_username, first=True, group=group)
        entry.title = username
        entry.username = username
        entry.password = password
        entry.set_custom_property(EXEGOL_DB_HASH_PROPERTY, hash, protect=True)
        entry.set_custom_property(EXEGOL_DB_DOMAIN_PROPERTY, domain, protect=True)
    except Exception:
        pass

    kp.save()
