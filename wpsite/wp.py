import io
import logging
import re
import xml.etree.ElementTree as ElementTree

from functools import reduce
from typing import Any, Callable, Generator

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


def tag_parser(element: ElementTree.Element) -> dict[str, list[str]]:
    path = 'category[@domain="post_tag"]'

    def tags(element: ElementTree.Element) -> Generator[str, None, None]:
        for child in element.iterfind(path, namespaces):
            yield child.attrib['nicename']

    return {'tags': list(tags(element))}


def parse_metadata(element: ElementTree.Element, key: str) -> str:
    path = f'wp:postmeta/wp:meta_key[.="{key}"]/.../wp:meta_value'
    meta_value = element.find(path, namespaces)
    if meta_value is not None and meta_value.text:
        return meta_value.text
    raise RuntimeError(f"Couldn't find <wp:meta_value> for key {key}")


def thumbnail_parser(attachments: dict[str, str]) -> Callable:
    def parser(element: ElementTree.Element) -> dict[str, str]:
        try:
            thumbnail_id = parse_metadata(element, '_thumbnail_id')
        except RuntimeError as e:
            logging.warning(str(e))
            return {}
        else:
            return {'thumbnail': attachments[thumbnail_id]}

    return parser


def parse_post(
    element: ElementTree.Element, parsers: list[Callable] = []
) -> dict:
    defaults = {
        'title': text_of(element, 'title'),
        'slug': text_of(element, 'wp:post_name'),
        'pubDate': text_of(element, 'wp:post_date_gmt'),
        'content': text_of(element, 'content:encoded'),
        'tags': '',
    }
    return reduce(
        lambda d, parser: {**d, **parser(element)}, parsers, defaults
    )


def items_of_type(
    source: io.TextIOBase, post_type: str
) -> Generator[ElementTree.Element, None, None]:
    for _, element in ElementTree.iterparse(source):
        if element.tag == 'item':
            if text_of(element, 'wp:post_type') == post_type:
                yield element


def posts(
    source: io.TextIOBase,
    filters: list[Callable[[str], str]] = [],
    parsers: list[Callable[[ElementTree.Element], dict[str, Any]]] = [],
) -> Generator[Page, None, None]:
    source.seek(0)
    for element in items_of_type(source, 'post'):
        if text_of(element, 'wp:status') == 'publish':
            yield Page(filters=filters, **parse_post(element, parsers))


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


class RemoveImageLinksFilter:
    """Remove links that navigate to wrapped image

    Some of the pages in a site I'm moving off WordPress contain <a> tags that
    wrap <img> tags. That's no problem in itself, but the href attribute of these
    <a> tags are set to the image that's displayed inside the link. At least
    for this site, that's pointless.

    """

    linked_image = re.compile(
        r'<a[^>]+\bhref="([^"]+)[^>]*?>(<img[^>]+\bsrc="\1"[^>]*?>)</a>'
    )

    def __call__(self, text: str) -> str:
        return self.linked_image.sub(r'\2', text)


class IllustratedParagraphFilter:
    """Insert line break after image at start of paragraph

    WordPress's editor makes it easy for people to create paragraphs that start
    with an image that then immediately run straight into some text, without
    any whitespace. In general I don't feel that the image is intended to be
    part of the paragraph that follows. This filter inserts a line break
    between them.

    """

    leading_image = re.compile(r'^(<img[^>]+>)([^\s])', flags=re.MULTILINE)

    def __call__(self, text: str) -> str:
        return self.leading_image.sub(r'\1\n\n\2', text)


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
