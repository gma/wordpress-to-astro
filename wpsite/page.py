import dataclasses
import html.parser
import re
import typing

import markdownify  # type: ignore


class ContentParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attachment_ids: set[str] = set()

    def _record_attachment_id(self, classes: str) -> None:
        for html_class in classes.split():
            if html_class.startswith('wp-image-'):
                self.attachment_ids.add(html_class.rsplit('-', 1)[-1])

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
    tags: list[str]
    content: str

    gallery_pattern = re.compile(r'\[gallery ids="([0-9,]+)[^]]+\]')

    def markdown(self, filters: list[typing.Callable]) -> str:
        html = self.content
        for func in filters:
            html = func(html)
        return markdownify.markdownify(html)

    @property
    def inline_image_ids(self) -> set[str]:
        parser = ContentParser()
        parser.feed(self.content)
        parser.close()
        return set(parser.attachment_ids)

    @property
    def gallery_image_ids(self) -> set[str]:
        attachment_ids = set()
        for id_list in re.findall(self.gallery_pattern, self.content):
            for attachment_id in id_list.split(','):
                attachment_ids.add(attachment_id)
        return attachment_ids

    @property
    def attachment_ids(self) -> set[str]:
        return self.inline_image_ids.union(self.gallery_image_ids)
