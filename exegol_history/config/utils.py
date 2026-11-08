from importlib.resources import files
from pathlib import Path


def write_file(output_path: str, anchor_name: str, filename: str):
    if not Path(output_path).exists():
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)

        with open(output_path, "w") as data_file:
            data = files(anchor_name).joinpath(filename)
            data_file.write(data.read_text("utf-8"))
