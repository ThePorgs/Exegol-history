import pyperclip
import subprocess
import platform

ID_DELIMITER = ","
ID_RANGE_DELIMITER = "-"

MESSAGE_ID_NOT_EXIST = "The provided id does not exist !"


def copy_in_clipboard(input: str):
    # Reference:
    # https://stackoverflow.com/questions/48499398/how-to-run-a-process-and-quit-after-the-script-is-over
    # https://github.com/kovidgoyal/kitty/issues/828

    # Pyperclip doesn't seems to provide public
    # API access to the primary argument
    # so we must manually do it
    if platform.system() == "Linux":
        subprocess.run(
            ["xclip", "-selection", "primary"],
            input=input.encode("utf-8"),
            stdout=subprocess.DEVNULL,
        )

    pyperclip.copy(input)


def parse_ids(input: str) -> list[int]:
    ids = set()
    parts = input.split(ID_DELIMITER)

    for part in parts:
        part = part.strip()

        try:
            if ID_RANGE_DELIMITER in part:
                start, end = map(int, part.split(ID_RANGE_DELIMITER))
                if start <= end:
                    ids.update(range(start, end + 1))
            else:
                ids.add(int(part))
        except ValueError:
            continue

    return list(ids)
