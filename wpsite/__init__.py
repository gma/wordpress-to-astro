from pathlib import Path


def convert_to_markdown(xml_file: Path, content_dir: Path) -> None:
    content_dir.mkdir(exist_ok=True, parents=True)
