import typing

from pathlib import Path
from unittest import mock

import pytest

import wpsite


@pytest.fixture(autouse=True)
def stub_urlopen() -> typing.Generator[None, None, None]:
    # We're stubbing out calls to urllib.request.urlopen(), which is used to
    # download files that are attached to pages/posts.
    #
    # urlopen() really returns an instance of http.client.HTTPResponse,
    # which inherits the interface that we want to use from io.BytesIO.
    #
    # So we can stub out read() from the BytesIO interface instead of getting
    # involved with sockets/socket-like objects.
    #
    with mock.patch.object(wpsite.astro.urllib.request, 'urlopen') as stub:
        stub.return_value.read.return_value = b'response data'
        yield


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    return tmp_path / 'src' / 'content' / 'blog'


def test_creates_content_dir(xml_file: Path, content_dir: Path) -> None:
    wpsite.convert_to_markdown(xml_file, content_dir)

    assert content_dir.exists()
    assert content_dir.is_dir()


def test_creates_markdown(xml_file: Path, content_dir: Path) -> None:
    post_slug = 'the-art-of-connection'
    post_filename = (content_dir / post_slug / 'index').with_suffix('.md')

    wpsite.convert_to_markdown(xml_file, content_dir)

    assert post_filename.exists()
    assert post_filename.is_file()


def test_fetches_attachments(xml_file: Path, content_dir: Path) -> None:
    post_slug = 'the-art-of-connection'
    attachment_path = content_dir / post_slug / 'image.jpg'

    wpsite.convert_to_markdown(xml_file, content_dir)

    assert attachment_path.exists(), f'{attachment_path} should exist'
