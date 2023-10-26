from pathlib import Path

from .page import Page


def create_page(content_dir: Path, post: Page) -> None:
    content_dir.mkdir(exist_ok=True, parents=True)

    filename = (content_dir / post.slug).with_suffix('.md')

    with filename.open('w') as file:
        file.write(
            f"""---
title: {post.title}
pubDate: {post.pubDate}
---
"""
        )
