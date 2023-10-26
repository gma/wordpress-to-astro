from pathlib import Path

from .context import astro
from .context import page


def test_markdown_files_are_created(tmp_path: Path) -> None:
    content_dir = tmp_path / 'content'
    post = page.Page(title='Title', slug='slug')

    astro.create_page(content_dir, post)

    filename = (content_dir / post.slug).with_suffix('.md')
    assert filename.is_file()
