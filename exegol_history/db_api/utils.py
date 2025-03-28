import subprocess
import re

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


def write_in_profile(variables_correspondance):
    with open(PROFILE_SH_PATH, "r") as profile:
        variables = profile.readlines()

        for i, line in enumerate(variables):
            tmp = re.search(VARIABLE_REGEX, line)

            if tmp:
                variable_name = tmp.group(1)

                if variable_name in variables_correspondance.keys():
                    line = f"export {variable_name}='{variables_correspondance[variable_name]}'\n"
                    variables[i] = line

            with open(PROFILE_SH_PATH, "w") as profile:
                profile.write("".join(variables))
