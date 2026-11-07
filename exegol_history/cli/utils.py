import re
import platform
from pathlib import Path
from typing import Dict, Union
from exegol_history.config.config import AppConfig
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.db_api.kerberos import Ticket
from exegol_history.cli.arguments import check_delimiter  # noqa: F401 (re-export)
import json
from rich.markup import escape
import os
import tempfile

CREDS_VARIABLES = ["USER", "PASSWORD", "NT_HASH", "DOMAIN"]
HOSTS_VARIABLES = ["IP", "TARGET", "DB_HOSTNAME", "DC_HOST", "DC_IP", "ROLE"]
KERBEROS_VARIABLES = ["USER", "DOMAIN", "KRB5CCNAME", "PASSWORD", "NT_HASH"]
VARIABLE_REGEX_UNIX = r"(?:export|unset) ([\w\d]*)(?:='.*?')?"
VARIABLE_REGEX_WINDOWS = r"(?:Set|Remove)-Variable -Name (\S*) (?:-Value '[^']*?' )?-Scope Global(?: -ErrorAction SilentlyContinue)?"


def write_host_in_profile(host: Host, config: AppConfig):
    data_path = config.paths.data_path
    variables_correspondance = {
        "IP": host.ip,
        "TARGET": host.ip,
        "DB_HOSTNAME": host.hostname,
    }

    if host.role == "DC":
        variables_correspondance["DC_HOST"] = host.hostname
        variables_correspondance["DC_IP"] = host.ip

    parse_and_update(data_path, variables_correspondance)


def write_credential_in_profile(credential: Credential, config: AppConfig):
    data_path = config.paths.data_path
    variables_correspondance = {
        "USER": credential.username,
        "PASSWORD": credential.password,
        "NT_HASH": credential.hash,
        "DOMAIN": credential.domain,
    }

    parse_and_update(data_path, variables_correspondance)


def write_kerberos_in_profile(ticket: Ticket, config: AppConfig):
    data_path = config.paths.data_path
    # Setting a Kerberos ticket sets USER/DOMAIN/KRB5CCNAME and clears any
    # password or NT hash currently set since we now authenticate with a ticket.
    variables_correspondance = {
        "USER": ticket.username,
        "DOMAIN": ticket.domain,
        "KRB5CCNAME": ticket.path,
        "PASSWORD": None,
        "NT_HASH": None,
    }

    parse_and_update(data_path, variables_correspondance)


def parse_and_update(
    data_path: Union[str, Path], variables_correspondance: Dict[str, str]
):
    with open(data_path, "r", encoding="utf-8") as profile:
        profile_json = json.load(profile)

    for variable_name, variable_value in variables_correspondance.items():
        profile_json[variable_name] = variable_value

    fd, tmp = tempfile.mkstemp(dir=Path(data_path).parent, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(profile_json, f, indent=2, ensure_ascii=False)
        os.replace(tmp, data_path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _console_message(symbol: str, color: str, message) -> str:
    return f"[[bold {color}]{symbol}[/bold {color}]] {escape(str(message))}"


def console_error(message) -> str:
    return _console_message("!", "red", message)


def console_success(message) -> str:
    return _console_message("+", "green", message)


def console_info(message) -> str:
    return _console_message("*", "blue", message)

