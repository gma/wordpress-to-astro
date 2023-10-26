from pathlib import Path


from . import astro
from . import page
from . import wp


def convert_to_markdown(xml_file: Path, content_dir: Path) -> None:
    with xml_file.open() as file:
        for post in wp.posts(file):
            astro.create_page(content_dir, post)
