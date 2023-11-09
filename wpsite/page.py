import dataclasses
import html.parser
import re


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


class HtmlConverter(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.heading_level: int | None = None

    @property
    def markdown(self) -> str:
        return '\n\n'.join(self.parts)

    def _handle_headings(self, tag: str) -> None:
        match = re.match(r'h([0-6])$', tag)
        if match:
            self.heading_level = int(match.group(1))

    def _handle_images(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == 'img':
            alt = src = ''
            for attr, value in attrs:
                if attr == 'alt' and value is not None:
                    alt = value
                if attr == 'src' and value is not None:
                    src = value
            self.parts.append(f'![{alt}]({src})')

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._handle_headings(tag)
        self._handle_images(tag, attrs)

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if len(stripped):
            if self.heading_level:
                stripped = ' '.join(('#' * self.heading_level, stripped))
                self.heading_level = None
            self.parts.append(stripped)


@dataclasses.dataclass
class Page:
    title: str
    slug: str
    pubDate: str
    tags: list[str]
    content: str

    @property
    def markdown(self) -> str:
        parser = HtmlConverter()
        parser.feed(self.content)
        parser.close()
        return parser.markdown

    @property
    def inline_image_ids(self) -> set[str]:
        parser = ContentParser()
        parser.feed(self.content)
        parser.close()
        return set(parser.attachment_ids)

    @property
    def gallery_image_ids(self) -> set[str]:
        attachment_ids = set()
        for id_list in re.findall(r'\[gallery ids="([0-9,]+)', self.content):
            for attachment_id in id_list.split(','):
                attachment_ids.add(attachment_id)
        return attachment_ids

    @property
    def attachment_ids(self) -> set[str]:
        return self.inline_image_ids.union(self.gallery_image_ids)
