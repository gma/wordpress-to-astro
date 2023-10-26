from pathlib import Path

from .page import Page


def create_page(content_dir: Path, post: Page) -> None:
    content_dir.mkdir(exist_ok=True, parents=True)

    filename = (content_dir / post.slug).with_suffix('.md')

    filename.touch(exist_ok=False)
