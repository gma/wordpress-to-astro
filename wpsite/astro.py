from pathlib import Path

from .page import Page


def escape_quotes(text: str) -> str:
    return '"' + text.replace('"', '\\"') + '"'


def create_page(content_dir: Path, post: Page) -> None:
    content_dir.mkdir(exist_ok=True, parents=True)

    filename = (content_dir / post.slug).with_suffix('.md')

    with filename.open('w') as file:
        file.write(
            f"""---
title: {escape_quotes(post.title)}
pubDate: {post.pubDate}
---
{post.content}
"""
        )
