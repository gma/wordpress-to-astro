from pathlib import Path

import pytest

import wpsite


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    return tmp_path / 'src' / 'content' / 'blog'


def test_convert_creates_content_dir(
    xml_file: Path, content_dir: Path
) -> None:
    wpsite.convert_to_markdown(xml_file, content_dir)

    assert content_dir.exists()
    assert content_dir.is_dir()


@pytest.mark.skip('pending')
def test_convert_creates_files_for_posts(
    xml_file: Path, content_dir: Path
) -> None:
    post_slug = 'the-art-of-connection'
    post_filename = (content_dir / post_slug).with_suffix('.md')

    wpsite.convert_to_markdown(xml_file, content_dir)

    assert post_filename.exists()
    assert post_filename.is_file()
