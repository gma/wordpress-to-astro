import dataclasses
import html.parser
import re


class ContentParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attachment_ids: list[str] = []

    def _record_attachment_id(self, classes: str) -> None:
        for html_class in classes.split():
            if html_class.startswith('wp-image-'):
                self.attachment_ids.append(html_class.rsplit('-', 1)[-1])

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

    def _inline_image_ids(self) -> list[str]:
        parser = ContentParser()
        parser.feed(self.content)
        parser.close()
        return parser.attachment_ids

    def _gallery_image_ids(self) -> list[str]:
        attachment_ids = []
        for id_list in re.findall(r'\[gallery ids="([0-9,]+)', self.content):
            for attachment_id in id_list.split(','):
                attachment_ids.append(attachment_id)
        return attachment_ids

    @property
    def attachment_ids(self) -> list[str]:
        return self._inline_image_ids() + self._gallery_image_ids()
