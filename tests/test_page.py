import re

from .context import page


class TestContentParser:
    def test_records_ids_of_images_with_wp_image_class(self) -> None:
        image_id = '1234'
        content = f"""
<img class="alignnone size-full wp-image-{image_id}" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!
"""

        parser = page.ContentParser()
        parser.feed(content)
        parser.close()

        assert parser.attachment_ids == set([image_id])


class TestHtmlConverter:
    def test_discards_comments(self) -> None:
        content = '<!-- wp:paragraph -->'

        converter = page.HtmlConverter()
        converter.feed(content)
        converter.close()

        assert 'wp:paragraph' not in converter.markdown

    def test_converts_p_tag_style_paragraphs(self) -> None:
        # As of the time of writing, this markup is used in recently authored
        # WordPress pages
        content = """
<!-- wp:paragraph -->
<p>Paragraph 1</p>
<!-- wp:paragraph -->

<!-- wp:paragraph -->
<p>Paragraph 2</p>
<!-- wp:paragraph -->
"""

        converter = page.HtmlConverter()
        converter.feed(content)
        converter.close()

        assert converter.markdown == 'Paragraph 1\n\nParagraph 2'

    def test_converts_span_tag_style_paragraphs(self) -> None:
        # This markup has been used in older pages that I've recently exported
        # from WordPress
        content = """
<span style="font-weight:400;">Paragraph 1</span>

<span style="font-weight:400;">Paragraph 2</span>
"""

        converter = page.HtmlConverter()
        converter.feed(content)
        converter.close()

        assert converter.markdown == 'Paragraph 1\n\nParagraph 2'

    def test_converts_headings(self) -> None:
        content = """
<h1>H1</h1>
<h2>H2</h2>
<h3>H3</h3>
"""

        converter = page.HtmlConverter()
        converter.feed(content)
        converter.close()

        assert converter.markdown == '# H1\n\n## H2\n\n### H3'


class TestPage:
    def test_converts_current_wp_html_content_to_markdown(self) -> None:
        content = """
<!-- wp:paragraph -->
<p>This is an example of a page. Unlike posts, which are displayed on your blog’s front page in the order they’re published, pages are better suited for more timeless content that you want to be easily accessible, like your About or Contact information.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<img class="alignnone size-full wp-image-1234" alt="Alt text" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!
<!-- /wp:paragraph -->
"""

        post = page.Page('Title', 'slug', '2023-10-30', [], content)
        markdown = post.markdown

        assert re.search('^This is an example', markdown)
        assert re.search(
            '^!\\[Alt text\\]\\(https', markdown, flags=re.MULTILINE
        )

    def test_finds_ids_of_inline_images(self) -> None:
        image_id = '1234'
        content = f"""
<img class="alignnone size-full wp-image-{image_id}" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!
"""

        post = page.Page('Title', 'slug', '2023-10-30', [], content)

        assert post.attachment_ids == set([image_id])

    def test_finds_ids_of_gallery_images(self) -> None:
        image_1 = '123'
        image_2 = '456'
        image_3 = '789'
        content = f"""
[gallery ids="{image_1}" type="rectangular"]

[gallery ids="{image_2},{image_3}" type="rectangular"]
"""

        post = page.Page('Title', 'slug', '2023-10-30', [], content)

        assert post.attachment_ids == set([image_1, image_2, image_3])
