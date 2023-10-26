import dataclasses


@dataclasses.dataclass
class Page:
    title: str
    slug: str
    pubDate: str
