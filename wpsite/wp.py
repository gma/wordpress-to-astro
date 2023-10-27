import io
import typing
import xml.etree.ElementTree

from .page import Page


namespaces = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
}


def tag_text(element: xml.etree.ElementTree.Element, tag: str) -> str:
    child = element.find(tag, namespaces)
    if child is not None:
        return '' if child.text is None else child.text
    raise ValueError(f"Couldn't find {tag} beneath {element.tag}")


def parse_post(element: xml.etree.ElementTree.Element) -> dict:
    return {
        'title': tag_text(element, 'title'),
        'slug': tag_text(element, 'wp:post_name'),
        'pubDate': tag_text(element, 'wp:post_date_gmt'),
        'content': tag_text(element, 'content:encoded'),
    }


def posts(source: io.TextIOBase) -> typing.Generator[Page, None, None]:
    for _, element in xml.etree.ElementTree.iterparse(source):
        if element.tag == 'item':
            if tag_text(element, 'wp:post_type') == 'post':
                if tag_text(element, 'wp:status') == 'publish':
                    yield Page(**parse_post(element))
