from pathlib import Path

import pytest

from .context import astro
from .context import page


@pytest.fixture
def post() -> page.Page:
    return page.Page(
        title='Title',
        slug='slug',
        pubDate='2023-10-24 15:25:27',
        content='The post',
    )


def test_markdown_files_are_created(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    astro.create_page(content_dir, post)

    filename = (content_dir / post.slug).with_suffix('.md')
    assert filename.is_file()


def test_yaml_frontmatter_is_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    astro.create_page(content_dir, post)

    filename = (content_dir / post.slug).with_suffix('.md')
    with filename.open() as f:
        text = f.read()

        assert '---\n' in text
        assert f'title: {post.title}' in text
