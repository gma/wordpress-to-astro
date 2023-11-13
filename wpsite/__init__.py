from pathlib import Path


from . import astro
from . import page
from . import wp


def convert_to_markdown(xml_file: Path, content_dir: Path) -> None:
    with xml_file.open() as file:
        attachments = wp.attachments_by_id(file)
        for post in wp.posts(
            file,
            [
                wp.DeSpanFilter(),
                wp.RemoveImageLinksFilter(),
                wp.IllustratedParagraphFilter(),
                wp.GalleryFilter(attachments),
                astro.HostedImageFilter(attachments),
            ],
        ):
            post_dir = astro.PostDirectory(content_dir, post)
            post_dir.create_markdown()
            post_dir.fetch_attachments(attachments)
