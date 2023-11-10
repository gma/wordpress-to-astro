import logging
import re
import urllib.parse
import urllib.request

from pathlib import Path, PurePath

from .page import AttachmentParser, Page


class PostDirectory:
    def __init__(self, content_dir: Path, post: Page) -> None:
        self.content_dir = content_dir
        self.post = post
        self.path = self.content_dir / post.slug

    def escape_quotes(self, text: str) -> str:
        return '"' + text.replace('"', '\\"') + '"'

    @property
    def markdown_filename(self) -> Path:
        return (self.path / 'index').with_suffix('.md')

    def create_post_dir(self) -> None:
        self.markdown_filename.parent.mkdir(exist_ok=True, parents=True)

    def create_markdown(self) -> None:
        self.create_post_dir()

        text = f"""---
title: {self.escape_quotes(self.post.title)}
pubDate: {self.post.pubDate}
"""
        if self.post.tags:
            text += '\n'.join(['tags:'] + [f'  - {t}' for t in self.post.tags])

        text += f"""
---
{self.post.markdown}
"""
        with self.markdown_filename.open('w') as file:
            file.write(text)

    def attachment_basename(self, url: str) -> str:
        return PurePath(urllib.parse.urlparse(url).path).name

    def save_image(self, url: str) -> None:
        image_file = self.path / self.attachment_basename(url)
        if image_file.exists():
            logging.debug(f'Skipping {url} (file exists)')
        else:
            logging.info(f'Downloading {url}')
            with open(image_file, 'wb') as f:
                f.write(urllib.request.urlopen(url).read())

    def fetch_attachments(self, attachment_urls: dict[str, str]) -> None:
        self.create_post_dir()
        logging.info(f'Fetching attachments for {self.post.slug}')
        for attachment_id in self.post.attachment_ids:
            try:
                url = attachment_urls[attachment_id]
            except KeyError:
                logging.warning(
                    f'Attachment missing from export: {attachment_id}'
                )
            else:
                self.save_image(url)


class HostedImageFilter:
    def __init__(self, attachment_urls: dict[str, str]) -> None:
        self.attachment_urls = attachment_urls

    def __call__(self, text: str) -> str:
        self.text = text
        parser = AttachmentParser(self.replace_url)
        parser.feed(text)
        parser.close()
        return self.text

    def replace_url(self, attachment_id: str) -> None:
        try:
            url = self.attachment_urls[attachment_id]
        except KeyError:
            logging.warning(f'Attachment missing from export: {attachment_id}')
        else:
            basename = PurePath(urllib.parse.urlparse(url).path).name
            self.text = re.sub(rf'{url}(\?[^"]+)?', f'./{basename}', self.text)
