import subprocess


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
