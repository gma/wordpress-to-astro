import dataclasses
import html.parser


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

    @property
    def attachment_ids(self) -> list[str]:
        parser = ContentParser()
        parser.feed(self.content)
        parser.close()
        return parser.attachment_ids
