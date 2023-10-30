import io
import xml.etree.ElementTree as ElementTree

from typing import Generator

from .page import Page


namespaces = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
}


def text_of(element: ElementTree.Element, tag: str) -> str:
    child = element.find(tag, namespaces)
    if child is not None:
        return '' if child.text is None else child.text
    raise ValueError(f"Couldn't find {tag} beneath {element.tag}")


def parse_tags(element: ElementTree.Element) -> list[str]:
    path = 'category[@domain="post_tag"]'

    def tags(element: ElementTree.Element) -> Generator[str, None, None]:
        for child in element.iterfind(path, namespaces):
            yield child.attrib['nicename']

    return list(tags(element))


def parse_post(element: ElementTree.Element) -> dict:
    return {
        'title': text_of(element, 'title'),
        'slug': text_of(element, 'wp:post_name'),
        'pubDate': text_of(element, 'wp:post_date_gmt'),
        'tags': parse_tags(element),
        'content': text_of(element, 'content:encoded'),
    }


def posts(source: io.TextIOBase) -> Generator[Page, None, None]:
    for _, element in ElementTree.iterparse(source):
        if element.tag == 'item':
            if text_of(element, 'wp:post_type') == 'post':
                if text_of(element, 'wp:status') == 'publish':
                    yield Page(**parse_post(element))
