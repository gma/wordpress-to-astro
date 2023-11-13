from unittest import mock

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


photo_attachment_id = '123'


@pytest.fixture
def photo_post() -> page.Page:
    return page.Page(
        title='Title',
        slug='slug',
        pubDate='2023-10-24 15:25:27',
        tags=[],
        content=f"""
Some text with attached image.

<img class="wp-image-{photo_attachment_id}" src="...">
""",
    )


def test_markdown_files_are_created(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    filename = (content_dir / post.slug / 'index').with_suffix('.md')
    assert filename.is_file()


def markdown_file_text(dir: Path, page: page.Page) -> str:
    filename = (dir / page.slug / 'index').with_suffix('.md')
    with filename.open() as f:
        return f.read()


def test_yaml_frontmatter_is_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = markdown_file_text(content_dir, post)
    assert '---\n' in text
    assert f'title: "{post.title}"' in text


def test_tags_omitted_by_default(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = markdown_file_text(content_dir, post)
    assert 'tags:' not in text


def test_tags_listed_when_set(tmp_path: Path, tagged_post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, tagged_post)
    post_dir.create_markdown()

    text = markdown_file_text(content_dir, tagged_post)
    tag_yaml = """tags:
  - a-tag
  - another-tag"""
    assert tag_yaml in text


def test_yaml_syntax_is_escaped(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'
    post.title = '"A quote"'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    assert 'title: "\\"A quote\\""' in markdown_file_text(content_dir, post)


def test_thumbnail_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'
    basename = 'image.jpg'
    url = f'https://site/path/{basename}'
    post.thumbnail = url

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    assert f'coverImage: ./{basename}' in markdown_file_text(content_dir, post)


def test_post_content_is_included(tmp_path: Path, post: page.Page) -> None:
    content_dir = tmp_path / 'content'

    post_dir = astro.PostDirectory(content_dir, post)
    post_dir.create_markdown()

    text = markdown_file_text(content_dir, post)
    assert 'The post' in text


@mock.patch.object(astro.urllib.request, 'urlopen', autospec=True)
def test_attachments_fetched(
    mock_urlopen: mock.MagicMock, tmp_path: Path, photo_post: page.Page
) -> None:
    content_dir = tmp_path / 'content'
    post_dir = astro.PostDirectory(content_dir, photo_post)

    photo_bytes = b'some pixels'
    mock_urlopen.return_value.read.return_value = photo_bytes

    photo_filename = 'image.jpg'
    url = f'https://sitename.files.wordpress.com/{photo_filename}'

    post_dir.fetch_attachments({photo_attachment_id: url})

    mock_urlopen.assert_called_with(url)
    assert (post_dir.path / photo_filename).read_bytes() == photo_bytes


class TestHostedImageFilter:
    def test_replaces_wordpress_url_with_relative_path(self) -> None:
        image_id = '1234'
        basename = 'image.jpg'
        url = f'https://sitename.files.wordpress.com/{basename}'
        attachments = {image_id: url}
        content = f'<img class="wp-image-{image_id}" src="{url}">'

        text = astro.HostedImageFilter(attachments)(content)

        assert text == f'<img class="wp-image-{image_id}" src="./{basename}">'

    def test_replaces_urls_that_dont_use_ssl(self) -> None:
        image_id = '1234'
        basename = 'image.jpg'
        url = f'sitename.files.wordpress.com/{basename}'
        urls = {image_id: f'https://{url}'}
        content = f'<img class="wp-image-{image_id}" src="http://{url}">'

        text = astro.HostedImageFilter(urls)(content)

        assert text == f'<img class="wp-image-{image_id}" src="./{basename}">'

    def test_strips_image_size_parameters_from_query_string(self) -> None:
        image_id = '1234'
        basename = 'image.jpg'
        url = f'https://sitename.files.wordpress.com/{basename}'
        urls = {image_id: url}
        content = f'<img class="wp-image-{image_id}" src="{url}?w=1024">'

        text = astro.HostedImageFilter(urls)(content)

        assert text == f'<img class="wp-image-{image_id}" src="./{basename}">'
