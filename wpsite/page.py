import dataclasses


@dataclasses.dataclass
class Page:
    title: str
    slug: str
    pubDate: str
    tags: list[str]
    content: str
