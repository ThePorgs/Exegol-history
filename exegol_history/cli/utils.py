import argparse
import re
import platform
from pathlib import Path
from typing import Any, Dict, Union
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host

CREDS_VARIABLES = ["USER", "PASSWORD", "NT_HASH", "DOMAIN"]
HOSTS_VARIABLES = ["IP", "TARGET", "DB_HOSTNAME", "DC_HOST", "DC_IP", "ROLE"]
VARIABLE_REGEX_UNIX = r"(?:export|unset) ([\w\d]*)(?:='.*?')?"
VARIABLE_REGEX_WINDOWS = r"(?:Set|Remove)-Variable -Name (\S*) (?:-Value '[^']*?' )?-Scope Global(?: -ErrorAction SilentlyContinue)?"


def check_delimiter(delimiter: str) -> str:
    if len(delimiter) != 1:
        raise argparse.ArgumentTypeError("Delimiter must be a single character.")

    return delimiter


def write_host_in_profile(host: Host, config: dict[str, Any]):
    profile_sh_path = config["paths"]["profile_sh_path"]
    variables_correspondance = {
        HOSTS_VARIABLES[0]: host.ip,
        HOSTS_VARIABLES[1]: host.ip,
        HOSTS_VARIABLES[2]: host.hostname,
    }

    parse_and_update(profile_sh_path, variables_correspondance)


def write_credential_in_profile(credential: Credential, config: dict[str, Any]):
    profile_sh_path = config["paths"]["profile_sh_path"]
    variables_correspondance = {
        CREDS_VARIABLES[0]: credential.username,
        CREDS_VARIABLES[1]: credential.password,
        CREDS_VARIABLES[2]: credential.hash,
        CREDS_VARIABLES[3]: credential.domain,
    }

    parse_and_update(profile_sh_path, variables_correspondance)


def parse_and_update(profile_sh_path: Union[str, Path], variables_correspondance: Dict[str, str]):
    with open(profile_sh_path, "r") as profile:
        variables = profile.readlines()

    for i, line in enumerate(variables):
        if platform.system() == "Windows":
            tmp = re.search(VARIABLE_REGEX_WINDOWS, line)
        else:
            tmp = re.search(VARIABLE_REGEX_UNIX, line)

        if tmp:
            variable_name = tmp.group(1)

            if variable_name in variables_correspondance.keys():
                new_value = variables_correspondance[variable_name]
                if new_value:
                    if platform.system() == "Windows":
                        line = f"Set-Variable -Name {variable_name} -Value '{new_value}' -Scope Global\n"
                    else:
                        line = f"export {variable_name}='{new_value}'\n"
                else:
                    if platform.system() == "Windows":
                        line = f"Remove-Variable -Name {variable_name} -Scope Global -ErrorAction SilentlyContinue\n"
                    else:
                        line = f"unset {variable_name}\n"

                variables[i] = line

    with open(profile_sh_path, "w") as profile:
        profile.write("".join(variables))


def console_error(message: str):
    return f"[[bold red]![/bold red]] {message}"
