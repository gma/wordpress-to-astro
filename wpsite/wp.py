import io
import re
import xml.etree.ElementTree as ElementTree

from typing import Callable, Generator

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


def items_of_type(
    source: io.TextIOBase, post_type: str
) -> Generator[ElementTree.Element, None, None]:
    for _, element in ElementTree.iterparse(source):
        if element.tag == 'item':
            if text_of(element, 'wp:post_type') == post_type:
                yield element


def posts(
    source: io.TextIOBase, filters: list[Callable[[str], str]] = []
) -> Generator[Page, None, None]:
    source.seek(0)
    for element in items_of_type(source, 'post'):
        if text_of(element, 'wp:status') == 'publish':
            yield Page(filters=filters, **parse_post(element))


def attachments_by_id(source: io.TextIOBase) -> dict[str, str]:
    source.seek(0)
    urls = {}
    for element in items_of_type(source, 'attachment'):
        the_id = text_of(element, 'wp:post_id')
        urls[the_id] = text_of(element, 'wp:attachment_url')
    return urls


class DeSpanFilter:
    """Tidy up WordPress paragraphs for markdownify

    markdownify treats `<span>Para</span>` on a line that's separated
    from surrounding text via blank lines as part of the same paragraph as the
    next block of text. We use this filter to remove WordPress's unnecessary
    spans before generating the Markdown.

    """

    span_start = re.compile(r'^<span[^>]*?>', flags=re.MULTILINE)
    span_end = re.compile(r'</span>$', flags=re.MULTILINE)

    def __call__(self, text: str) -> str:
        return self.span_start.sub('', self.span_end.sub('', text))


class GalleryFilter:
    gallery_pattern = re.compile(r'\[gallery ids="([0-9,]+)[^]]+\]')

    def __init__(self, attachment_urls: dict[str, str]) -> None:
        self.urls = attachment_urls

    def __call__(self, text: str) -> str:
        return re.sub(self.gallery_pattern, self.image_markup, text)

    def image_markup(self, match: re.Match) -> str:
        tags = []
        for attachment_id in match.group(1).split(','):
            try:
                url = self.urls[attachment_id]
            except KeyError:
                pass
            else:
                tag = f'<img class="wp-image-{attachment_id}" src="{url}">'
                tags.append(tag)
        return '\n\n'.join(tags)
