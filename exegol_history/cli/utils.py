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
    profile_sh_path = config.paths.profile_sh_path
    variables_correspondance = {
        HOSTS_VARIABLES[0]: host.ip,
        HOSTS_VARIABLES[1]: host.ip,
        HOSTS_VARIABLES[2]: host.hostname,
    }

    if host.role == "DC":
        variables_correspondance[HOSTS_VARIABLES[3]] = host.hostname
        variables_correspondance[HOSTS_VARIABLES[4]] = host.ip

    parse_and_update(profile_sh_path, variables_correspondance)


def write_credential_in_profile(credential: Credential, config: AppConfig):
    profile_sh_path = config.paths.profile_sh_path
    variables_correspondance = {
        CREDS_VARIABLES[0]: credential.username,
        CREDS_VARIABLES[1]: credential.password,
        CREDS_VARIABLES[2]: credential.hash,
        CREDS_VARIABLES[3]: credential.domain,
    }

    parse_and_update(profile_sh_path, variables_correspondance)


def write_kerberos_in_profile(ticket: Ticket, config: AppConfig):
    profile_sh_path = config.paths.profile_sh_path
    # Setting a Kerberos ticket sets USER/DOMAIN/KRB5CCNAME and clears any
    # password or NT hash currently set since we now authenticate with a ticket.
    variables_correspondance = {
        KERBEROS_VARIABLES[0]: ticket.username,
        KERBEROS_VARIABLES[1]: ticket.domain,
        KERBEROS_VARIABLES[2]: ticket.path,
        KERBEROS_VARIABLES[3]: None,
        KERBEROS_VARIABLES[4]: None,
    }

    parse_and_update(profile_sh_path, variables_correspondance)


def parse_and_update(
    data_path: Union[str, Path], variables_correspondance: Dict[str, str]
):
    with open(data_path, "r", encoding="utf-8") as profile:
        profile_json = json.load(profile)

    for variable_name, variable_value in variables_correspondance.items():
        profile_json[variable_name] = variable_value

    fd, tmp = tempfile.mkstemp(dir=Path(data_path).parent, suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(profile_json, f, indent=2, ensure_ascii=False)
    os.replace(tmp, data_path)


def console_error(message: str):
    return f"[[bold red]![/bold red]] {escape(str(message))}"


def console_success(message: str):
    return f"[[bold green]+[/bold green]] {escape(str(message))}"


def console_info(message: str):
    return f"[[bold blue]*[/bold blue]] {escape(str(message))}"
