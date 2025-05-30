from pykeepass import PyKeePass

GROUP_NAME_CREDENTIALS = "Credentials"
EXEGOL_DB_HASH_PROPERTY = "hash"
EXEGOL_DB_DOMAIN_PROPERTY = "domain"
REDACT_SEPARATOR = "*"


def add_credential(
    kp: PyKeePass, username: str, password: str = "", hash: str = "", domain: str = ""
):
    if not username:
        raise ValueError("Username cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)
    credentials = get_credentials(kp)

    if credentials:
        id = str(int(credentials[-1][0]) + 1)  # The next id is the last used id + 1
    else:
        id = "1"

    entry = kp.find_entries(
        username=username, string={EXEGOL_DB_DOMAIN_PROPERTY: domain}, group=group
    )

    if len(entry) == 1:
        edit_credential(kp, entry[0].title, username, password, hash, domain)
    else:
        entry = kp.add_entry(group, id, username, password)
        entry.set_custom_property(EXEGOL_DB_HASH_PROPERTY, hash, protect=True)
        entry.set_custom_property(EXEGOL_DB_DOMAIN_PROPERTY, domain, protect=True)

    kp.save()


def get_credentials(
    kp: PyKeePass,
    searched_id: str = None,
    searched_username: str = None,
    searched_password: str = None,
    searched_hash: str = None,
    searched_domain: str = None,
    redacted: bool = False,
) -> [(str, str, str, str, str)]:
    array = []
    custom_properties = {}

    if searched_domain:
        custom_properties[EXEGOL_DB_DOMAIN_PROPERTY] = searched_domain

    if searched_hash:
        custom_properties[EXEGOL_DB_HASH_PROPERTY] = searched_hash

    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)
    entries = kp.find_entries(
        title=searched_id,
        username=searched_username,
        password=searched_password,
        string=custom_properties,
        group=group,
    )

    for entry in entries:
        password = entry.password
        hash = entry.get_custom_property(EXEGOL_DB_HASH_PROPERTY)
        domain = entry.get_custom_property(EXEGOL_DB_DOMAIN_PROPERTY)

        if redacted:
            hash = password = REDACT_SEPARATOR * 10

        if not password:
            password = ""

        if not hash:
            hash = ""

        if not domain:
            domain = ""

        array.append((entry.title, entry.username, password, hash, domain))

    return array


def delete_credential(kp: PyKeePass, id: str):
    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)
    entry = kp.find_entries(title=id, first=True, group=group)

    if entry:
        kp.delete_entry(entry)
        kp.save()
    else:
        raise RuntimeError("The provided username does not exist")


def edit_credential(
    kp: PyKeePass,
    id: str,
    username: str,
    password: str = "",
    hash: str = "",
    domain: str = "",
):
    if not username:
        raise ValueError("Username cannot be empty")

    group = kp.find_groups(name=GROUP_NAME_CREDENTIALS, first=True)

    try:
        entry = kp.find_entries(title=id, first=True, group=group)
        entry.username = username
        entry.password = password
        entry.set_custom_property(EXEGOL_DB_HASH_PROPERTY, hash, protect=True)
        entry.set_custom_property(EXEGOL_DB_DOMAIN_PROPERTY, domain, protect=True)
    except Exception:
        pass

    kp.save()
