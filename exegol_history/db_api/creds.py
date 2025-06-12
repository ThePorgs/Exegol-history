from pykeepass import PyKeePass
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST


class Credential:
    GROUP_NAME = "Credentials"
    EXEGOL_DB_HASH_PROPERTY = "hash"
    EXEGOL_DB_DOMAIN_PROPERTY = "domain"
    REDACT_SEPARATOR = "*"
    HEADERS = ["username", "password", "hash", "domain"]

    def __init__(
        self,
        id: str = "",
        username: str = "",
        password: str = "",
        hash: str = "",
        domain: str = "",
    ):
        self.id = id
        self.username = username
        self.password = password
        self.hash = hash
        self.domain = domain

    def __iter__(self):
        return iter([self.id, self.username, self.password, self.hash, self.domain])

    # Convert a Keepass entry into a Credential object
    @staticmethod
    def credential_from_entry(entry, redacted: bool = False):
        if redacted:
            password = Credential.REDACT_SEPARATOR * 8
        elif entry.password:
            password = entry.password
        else:
            password = ""

        return Credential(
            entry.title if entry.title else "",
            entry.username if entry.username else "",
            password,
            entry.get_custom_property(Credential.EXEGOL_DB_HASH_PROPERTY)
            if entry.get_custom_property(Credential.EXEGOL_DB_HASH_PROPERTY)
            else "",
            entry.get_custom_property(Credential.EXEGOL_DB_DOMAIN_PROPERTY)
            if entry.get_custom_property(Credential.EXEGOL_DB_DOMAIN_PROPERTY)
            else "",
        )

    def __eq__(self, value):
        return (
            (self.id == value.id)
            and (self.username == value.username)
            and (self.password == value.password)
            and (self.hash == value.hash)
            and (self.domain == value.domain)
        )


def get_new_credential_id(kp: PyKeePass) -> str:
    credentials = get_credentials(kp)

    return str(int(credentials[-1].id) + 1) if credentials else "1"


def add_credentials(kp: PyKeePass, credentials: list[Credential]):
    for credential in credentials:
        add_credential(kp, credential)

    kp.save()


def add_credential(kp: PyKeePass, credential: Credential):
    id = get_new_credential_id(kp)
    credential.id = id

    group = kp.find_groups(name=Credential.GROUP_NAME, first=True)
    entry = kp.add_entry(group, id, credential.username, credential.password or "")
    entry.set_custom_property(
        Credential.EXEGOL_DB_HASH_PROPERTY, credential.hash, protect=True
    )
    entry.set_custom_property(
        Credential.EXEGOL_DB_DOMAIN_PROPERTY, credential.domain, protect=True
    )


def get_credentials(
    kp: PyKeePass, id: str = None, redacted: bool = False
) -> list[Credential]:
    group = kp.find_groups(name=Credential.GROUP_NAME, first=True)
    entries = kp.find_entries(title=id, recursive=True, group=group)

    return [Credential.credential_from_entry(entry, redacted) for entry in entries]


def delete_credentials(kp: PyKeePass, ids: list[str] = list()):
    for id in ids:
        delete_credential(kp, id)

    kp.save()


def delete_credential(kp: PyKeePass, id: str = ""):
    group = kp.find_groups(name=Credential.GROUP_NAME, first=True)
    entry = kp.find_entries(title=id, first=True, group=group)

    if entry:
        kp.delete_entry(entry)
    else:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)


def edit_credentials(kp: PyKeePass, credentials: list[Credential]):
    for credential in credentials:
        edit_credential(kp, credential)

    kp.save()


def edit_credential(kp: PyKeePass, credential: Credential):
    group = kp.find_groups(name=Credential.GROUP_NAME, first=True)
    entry = kp.find_entries(title=credential.id, first=True, group=group)

    if entry:
        entry.username = credential.username
        entry.password = credential.password
        entry.set_custom_property(
            Credential.EXEGOL_DB_HASH_PROPERTY, credential.hash, protect=True
        )
        entry.set_custom_property(
            Credential.EXEGOL_DB_DOMAIN_PROPERTY, credential.domain, protect=True
        )
    else:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)
