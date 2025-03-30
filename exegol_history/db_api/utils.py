import subprocess
import re

CREDS_VARIABLES = ["USER", "PASSWORD", "NT_HASH", "DOMAIN"]
HOSTS_VARIABLES = ["IP", "TARGET", "DB_HOSTNAME", "DC_HOST", "DC_IP"]
PROFILE_SH_PATH = "/opt/tools/Exegol-history/profile.sh"
VARIABLE_REGEX = r"export (.*)='.*?'"


def copy_in_clipboard(input: str):
    # Reference:
    # https://stackoverflow.com/questions/48499398/how-to-run-a-process-and-quit-after-the-script-is-over
    # https://github.com/kovidgoyal/kitty/issues/828
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=input.encode("utf-8"),
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["xclip", "-selection", "primary"],
        input=input.encode("utf-8"),
        stdout=subprocess.DEVNULL,
    )


def write_host_in_profile(profile_path, ip, hostname, role):
    variables_correspondance = {
        HOSTS_VARIABLES[0]: ip,
        HOSTS_VARIABLES[1]: ip,
        HOSTS_VARIABLES[2]: hostname,
    }

    if role == "DC":
        variables_correspondance[HOSTS_VARIABLES[3]] = hostname
        variables_correspondance[HOSTS_VARIABLES[4]] = ip

    with open(profile_path, "r") as profile:
        variables = profile.readlines()

        for i, line in enumerate(variables):
            tmp = re.search(VARIABLE_REGEX, line)

            if tmp:
                variable_name = tmp.group(1)

                if variable_name in variables_correspondance.keys():
                    line = f"export {variable_name}='{variables_correspondance[variable_name]}'\n"
                    variables[i] = line

            with open(profile_path, "w") as profile:
                profile.write("".join(variables))


def write_credential_in_profile(profile_path, username, password, hash, domain):
    variables_correspondance = {
        CREDS_VARIABLES[0]: username,
        CREDS_VARIABLES[1]: password,
        CREDS_VARIABLES[2]: hash,
        CREDS_VARIABLES[3]: domain,
    }

    with open(profile_path, "r") as profile:
        variables = profile.readlines()

        for i, line in enumerate(variables):
            tmp = re.search(VARIABLE_REGEX, line)

            if tmp:
                variable_name = tmp.group(1)

                if variable_name in variables_correspondance.keys():
                    line = f"export {variable_name}='{variables_correspondance[variable_name]}'\n"
                    variables[i] = line

            with open(profile_path, "w") as profile:
                profile.write("".join(variables))
