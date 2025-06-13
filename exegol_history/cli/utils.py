import argparse
import re
from typing import Any
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host

CREDS_VARIABLES = ["USER", "PASSWORD", "NT_HASH", "DOMAIN"]
HOSTS_VARIABLES = ["IP", "TARGET", "DB_HOSTNAME", "DC_HOST", "DC_IP"]
VARIABLE_REGEX = r"export (.*)='.*?'"


def check_delimiter(delimiter: str) -> str:
    if len(delimiter) != 1:
        raise argparse.ArgumentTypeError("Delimiter must be a single character.")

    return delimiter


def write_host_in_profile(host: Host, config: dict[str, Any]):
    variables_correspondance = {
        HOSTS_VARIABLES[0]: host.ip,
        HOSTS_VARIABLES[1]: host.ip,
        HOSTS_VARIABLES[2]: host.hostname,
    }
    profile_sh_path = config["paths"]["profile_sh_path"]

    if host.role == "DC":
        variables_correspondance[HOSTS_VARIABLES[3]] = host.hostname
        variables_correspondance[HOSTS_VARIABLES[4]] = host.ip

    with open(profile_sh_path, "r") as profile:
        variables = profile.readlines()

        for i, line in enumerate(variables):
            tmp = re.search(VARIABLE_REGEX, line)

            if tmp:
                variable_name = tmp.group(1)

                if variable_name in variables_correspondance.keys():
                    line = f"export {variable_name}='{variables_correspondance[variable_name]}'\n"
                    variables[i] = line

            with open(profile_sh_path, "w") as profile:
                profile.write("".join(variables))


def write_credential_in_profile(credential: Credential, config: dict[str, Any]):
    profile_sh_path = config["paths"]["profile_sh_path"]

    variables_correspondance = {
        CREDS_VARIABLES[0]: credential.username,
        CREDS_VARIABLES[1]: credential.password,
        CREDS_VARIABLES[2]: credential.hash,
        CREDS_VARIABLES[3]: credential.domain,
    }

    with open(profile_sh_path, "r") as profile:
        variables = profile.readlines()

        for i, line in enumerate(variables):
            tmp = re.search(VARIABLE_REGEX, line)

            if tmp:
                variable_name = tmp.group(1)

                if variable_name in variables_correspondance.keys():
                    line = f"export {variable_name}='{variables_correspondance[variable_name]}'\n"
                    variables[i] = line

            with open(profile_sh_path, "w") as profile:
                profile.write("".join(variables))


def console_error(message: str):
    return f"[[bold red]![/bold red]] {message}"
