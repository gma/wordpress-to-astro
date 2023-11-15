"""Convert WordPress export to Markdown suitable for Astro

WordPress sites can be exported [1] for migration to another WordPress host, or
for import into another CMS. The content of the pages in a WordPress site are
saved into an XML file.

The purpose of this Python package is to parse the WordPress XML and extract
the information that's required to move the site to a file-based or headless
CMS.

I've written the code with Astro [2] specifically in mind, but lots of
file-based CMS's format their pages in a very similar way, so this code could
be useful if you're moving a WordPress site to any file-based or headless CMS.

The code is organised into modules, each with a different area of
responsibility. This is the thinking behind what each module is for:

    - `wp` contains all the code that knows anything about WordPress's XML file;
      how to parse it and anything WordPress-specific

    - `page` contains code for modelling the CMS-agnostic concepts associated
      with a web page

    - `astro` knows how to convert the things in the `page` module into files
      that can be read by Astro

Think of `page` as a bridge between `wp` and `astro`. The code in `wp` takes
the XML and converts it into objects in `page`. Then the `astro` code can then
use things that live in `page` to build an Astro-ready representation of the
site. It's a way of separating the different "concerns" (see [3]).

If you'd like to see how they're glued together, have a look at the code in the
top-level of the `wpsite` package. That's really the entry point.

[1] https://wordpress.com/support/export/
[2] https://astro.build/
[3] https://en.wikipedia.org/wiki/Separation_of_concerns

"""

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
            [wp.tag_parser, wp.thumbnail_parser(attachments)],
        ):
            post_dir = astro.PostDirectory(content_dir, post)
            post_dir.create_markdown()
            post_dir.fetch_attachments(attachments)
