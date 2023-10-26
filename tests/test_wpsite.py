import pathlib

import wpsite


xml_fixture = pathlib.Path(__file__).parent / 'fixtures' / 'wordpress.xml'


def test_convert_creates_content_dir(tmp_path: pathlib.Path) -> None:
    content_dir = tmp_path / 'src' / 'content' / 'blog'

    wpsite.convert_to_markdown(xml_fixture, content_dir)

    assert content_dir.exists()
    assert content_dir.is_dir()
