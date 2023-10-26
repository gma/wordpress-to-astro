import io

from pathlib import Path

from .context import wp


def test_iterates_over_published_posts(xml_file: Path) -> None:
    source = io.StringIO(xml_file.open().read())

    post = next(wp.posts(source))

    assert post.title == 'The Art of Connection'
