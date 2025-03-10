from enum import Enum


class CredsFileType(Enum):
    CSV = 1
    PYPYKATZ_GREP = 2


class HostsFileType(Enum):
    CSV = 1
    NXC = 2


def parse_creds(creds_file_type: int, raw_text: str) -> []:
    try:
        match CredsFileType(creds_file_type):
            case CredsFileType.CSV:
                return parse_creds_comma(raw_text)
            case CredsFileType.PYPYKATZ_GREP:
                return parse_creds_pypykatz_greppable(raw_text)
    except Exception as e:
        raise ValueError(f"Failed to parse the content: {e}")

    return []


def parse_hosts(hosts_file_type: int, raw_text: str) -> []:
    try:
        match HostsFileType(hosts_file_type):
            case HostsFileType.CSV:
                return parse_hosts_comma(raw_text)
            case HostsFileType.NXC:
                return parse_hosts_nxc(raw_text)
    except Exception as e:
        raise e

    return []


def parse_hosts_comma(raw_text: str) -> []:
    parsed_hosts = []

    for line in raw_text.splitlines():
        if len(tuple(line.split(","))) != 3:
            raise ValueError("Values must be comma separated !")

        parsed_hosts.append(tuple(line.split(",")))

    return parsed_hosts


def parse_hosts_nxc(raw_text: str) -> []:
    parsed_hosts = []

    for line in raw_text.splitlines():
        # Skipping the last line
        if "Running nxc against" in line:
            continue
        tmp = tuple([line.split()[1], line.split()[3], ""])
        parsed_hosts.append(tmp)

    return parsed_hosts


def parse_creds_comma(raw_text: str) -> []:
    parsed_creds = []

    for line in raw_text.splitlines():
        if len(tuple(line.split(","))) != 4:
            raise ValueError("Values must be comma separated !")

        parsed_creds.append(tuple(line.split(",")))

    return parsed_creds


def parse_creds_pypykatz_greppable(raw_text: str) -> []:
    parsed_creds = {}
    parsed_creds2 = []

    for line in raw_text.splitlines():
        # Skipping the first line
        if "INFO:pypykatz" in line or "filename:packagename" in line:
            continue

        username = line.split(":")[3].lower()
        package_name = line.split(":")[1]
        if username != "" and "umfd-" not in username and "dwm-" not in username:
            if package_name == "msv":
                try:
                    parsed_creds[username]["username"] = username
                    parsed_creds[username]["hash"] = line.split(":")[4]
                    parsed_creds[username]["domain"] = line.split(":")[2]
                except KeyError:
                    parsed_creds[username] = {
                        "username": "",
                        "password": "",
                        "hash": "",
                        "domain": "",
                    }
                    parsed_creds[username]["username"] = username
                    parsed_creds[username]["hash"] = line.split(":")[4]
                    parsed_creds[username]["domain"] = line.split(":")[2]
            elif package_name == "wdigest":
                try:
                    parsed_creds[username]["password"] = line.split(":")[-1]
                except KeyError:
                    parsed_creds[username] = {
                        "username": "",
                        "password": "",
                        "hash": "",
                        "domain": "",
                    }
                    parsed_creds[username]["password"] = line.split(":")[-1]

    for key, value in parsed_creds.items():
        parsed_creds2.append(
            tuple(
                [
                    value["username"],
                    value["password"],
                    value["hash"],
                    value["domain"],
                ]
            )
        )

    return parsed_creds2
