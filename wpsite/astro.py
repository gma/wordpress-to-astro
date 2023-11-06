import logging
import urllib.parse
import urllib.request

from pathlib import Path, PurePath

from .page import Page


class PostDirectory:
    def __init__(self, content_dir: Path, post: Page) -> None:
        self.content_dir = content_dir
        self.post = post
        self.path = self.content_dir / post.slug

    def escape_quotes(self, text: str) -> str:
        return '"' + text.replace('"', '\\"') + '"'

    @property
    def filename(self) -> Path:
        return (self.path / 'index').with_suffix('.md')

    def create_post_dir(self) -> None:
        self.filename.parent.mkdir(exist_ok=True, parents=True)

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
{self.post.content}
"""
        with self.filename.open('w') as file:
            file.write(text)

    def fetch_attachments(self, urls: dict[str, str]) -> None:
        self.create_post_dir()
        logging.info(f'Fetching attachments for {self.post.slug}')
        for attachment_id in self.post.attachment_ids:
            try:
                url = urls[attachment_id]
            except KeyError:
                logging.warning(
                    f'Attachment missing from export: {attachment_id}'
                )
            else:
                logging.info(f'Downloading {url}')
                response = urllib.request.urlopen(url)
                data = response.read()
                basename = PurePath(urllib.parse.urlparse(url).path).name
                with open(self.path / basename, 'wb') as f:
                    f.write(data)
