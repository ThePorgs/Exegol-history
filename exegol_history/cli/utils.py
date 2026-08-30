import argparse
import re
import platform
from pathlib import Path
from typing import Dict, Union
from exegol_history.config.config import AppConfig
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host

CREDS_VARIABLES = ["CREDS_ID", "USER", "PASSWORD", "NT_HASH", "DOMAIN"]
HOSTS_VARIABLES = ["HOST_ID", "IP", "TARGET", "DB_HOSTNAME", "DC_HOST", "DC_IP", "ROLE"]
VARIABLE_REGEX_UNIX = r"(?:export|unset) ([\w\d]*)(?:='.*?')?"
VARIABLE_REGEX_WINDOWS = r"(?:Set|Remove)-Variable -Name (\S*) (?:-Value '[^']*?' )?-Scope Global(?: -ErrorAction SilentlyContinue)?"


def check_delimiter(delimiter: str) -> str:
    if len(delimiter) != 1:
        raise argparse.ArgumentTypeError("Delimiter must be a single character.")

    return delimiter


def write_host_in_profile(host: Host, config: AppConfig):
    profile_sh_path = config.paths.profile_sh_path
    variables_correspondance = {
        HOSTS_VARIABLES[0]: host.host_id,
        HOSTS_VARIABLES[1]: host.ip,
        HOSTS_VARIABLES[2]: host.ip,
        HOSTS_VARIABLES[3]: host.hostname,
    }

    if host.role == "DC":
        variables_correspondance[HOSTS_VARIABLES[4]] = host.hostname
        variables_correspondance[HOSTS_VARIABLES[5]] = host.ip

    parse_and_update(profile_sh_path, variables_correspondance)


def write_credential_in_profile(credential: Credential, config: AppConfig):
    profile_sh_path = config.paths.profile_sh_path
    variables_correspondance = {
        CREDS_VARIABLES[0]: credential.credential_id,
        CREDS_VARIABLES[1]: credential.username,
        CREDS_VARIABLES[2]: credential.password,
        CREDS_VARIABLES[3]: credential.hash,
        CREDS_VARIABLES[4]: credential.domain,
    }

    parse_and_update(profile_sh_path, variables_correspondance)


def parse_and_update(
    profile_sh_path: Union[str, Path], variables_correspondance: Dict[str, str]
):
    with open(profile_sh_path, "r") as profile:
        variables = profile.readlines()

    for i, line in enumerate(variables):
        # Search for the export line in the profile file
        if platform.system() == "Windows":
            tmp = re.search(VARIABLE_REGEX_WINDOWS, line)
        else:
            tmp = re.search(VARIABLE_REGEX_UNIX, line)

        if tmp:
            # extract the variable name from the regex match
            variable_name = tmp.group(1)
            if variable_name in variables_correspondance.keys():
                # replaces the line in the profile
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


def console_success(message: str):
    return f"[[bold green]+[/bold green]] {message}"


def console_info(message: str):
    return f"[[bold blue]*[/bold blue]] {message}"
