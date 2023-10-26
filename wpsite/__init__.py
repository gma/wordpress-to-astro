from pathlib import Path


from . import astro
from . import wp


def convert_to_markdown(xml_file: Path, content_dir: Path) -> None:
    content_dir.mkdir(exist_ok=True, parents=True)

    wordpress = wp.Site(xml_file)
    for post in wordpress.posts:
        astro.create_page(content_dir, post)
