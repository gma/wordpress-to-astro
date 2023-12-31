import dataclasses
import html.parser
import typing

from functools import reduce

import markdownify  # type: ignore


class AttachmentParser(html.parser.HTMLParser):
    def __init__(self, callback: typing.Callable) -> None:
        super().__init__()
        self.callback = callback

    def _record_attachment_id(self, classes: str) -> None:
        for html_class in classes.split():
            if html_class.startswith('wp-image-'):
                self.callback(html_class.rsplit('-', 1)[-1])

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == 'img':
            for attr, value in attrs:
                if attr == 'class' and value is not None:
                    self._record_attachment_id(value)
        return super().handle_starttag(tag, attrs)


@dataclasses.dataclass
class Page:
    title: str
    slug: str
    pubDate: str
    content: str
    tags: list[str] = dataclasses.field(default_factory=list)
    thumbnail: str = ''
    filters: list[typing.Callable[[str], str]] = dataclasses.field(
        default_factory=list
    )

    @property
    def filtered_html(self) -> str:
        return reduce(lambda html, f: f(html), self.filters, self.content)

    @property
    def markdown(self) -> str:
        return markdownify.markdownify(
            self.filtered_html, heading_style=markdownify.ATX
        )

    @property
    def attachment_ids(self) -> set[str]:
        ids = set()
        parser = AttachmentParser(lambda attachment_id: ids.add(attachment_id))
        parser.feed(self.filtered_html)
        parser.close()
        return ids
