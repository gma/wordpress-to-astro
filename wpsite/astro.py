from pathlib import Path

from .page import Page


class PostDirectory:
    def __init__(self, content_dir: Path, post: Page) -> None:
        self.content_dir = content_dir
        self.post = post

    def escape_quotes(self, text: str) -> str:
        return '"' + text.replace('"', '\\"') + '"'

    @property
    def filename(self) -> Path:
        return (self.content_dir / self.post.slug).with_suffix('.md')

    def create_markdown(self) -> None:
        self.content_dir.mkdir(exist_ok=True, parents=True)

        with self.filename.open('w') as file:
            file.write(
                f"""---
title: {self.escape_quotes(self.post.title)}
pubDate: {self.post.pubDate}
---
{self.post.content}
"""
            )
