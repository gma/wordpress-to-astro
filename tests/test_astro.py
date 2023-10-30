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
        tags=[],
        content='The post',
    )


@pytest.fixture
def tagged_post(post: page.Page) -> page.Page:
    post.tags = ['a-tag', 'another-tag']
    return post


def test_markdown_files_are_created(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    filename = (content_dir / post.slug).with_suffix('.md')
    assert filename.is_file()


def file_contents(dir: Path, page: page.Page) -> str:
    filename = (dir / page.slug).with_suffix('.md')
    with filename.open() as f:
        return f.read()


def test_yaml_frontmatter_is_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = file_contents(content_dir, post)
    assert '---\n' in text
    assert f'title: "{post.title}"' in text


def test_tags_omitted_by_default(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = file_contents(content_dir, post)
    assert 'tags:' not in text


def test_tags_listed_when_set(tmp_path: Path, tagged_post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, tagged_post)
    post_dir.create_markdown()

    text = file_contents(content_dir, tagged_post)
    tag_yaml = """tags:
  - a-tag
  - another-tag"""
    assert tag_yaml in text


def test_yaml_syntax_is_escaped(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'
    post.title = '"A quote"'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    assert 'title: "\\"A quote\\""' in file_contents(content_dir, post)


def test_post_content_is_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = file_contents(content_dir, post)
    assert 'The post' in text
