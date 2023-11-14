import io

import pytest

from .context import rss_doc
from .context import wp

attachment_id = '123'
attachment_url = 'https://sitename.files.wordpress.com/2023/10/image.jpg'


@pytest.fixture
def attachment_data() -> str:
    return f"""
<item>
  <title><![CDATA[FILE_BASENAME]]></title>
  <pubDate>Tue, 24 Oct 2023 15:25:20 +0000</pubDate>
  <description/>
  <wp:post_id>{attachment_id}</wp:post_id>
  <wp:post_date_gmt>2023-10-24 15:25:20</wp:post_date_gmt>
  <wp:post_name>file_basename</wp:post_name>
  <wp:status>inherit</wp:status>
  <wp:post_type>attachment</wp:post_type>
  <wp:attachment_url>{attachment_url}</wp:attachment_url>
</item>
"""


inline_image_id = '1234'
gallery_image_ids = ['123', '456']
thumbnail_id = '789'


@pytest.fixture
def post_data() -> str:
    return f"""
<item>
  <title><![CDATA[Post title]]></title>
  <pubDate>Tue, 24 Oct 2023 15:25:27 +0000</pubDate>
  <wp:post_date_gmt>2023-10-24 15:25:27</wp:post_date_gmt>
  <wp:post_name>post-name</wp:post_name>
  <wp:post_type>post</wp:post_type>
  <wp:status>publish</wp:status>
  <category domain="post_tag" nicename="tag-1"><![CDATA[tag 1]]></category>
  <category domain="post_tag" nicename="tag-2"><![CDATA[tag 2]]></category>
  <category domain="category" nicename="uncategorized"><![CDATA[Uncategorized]]></category>
  <wp:postmeta>
    <wp:meta_key>_thumbnail_id</wp:meta_key>
    <wp:meta_value><![CDATA[{thumbnail_id}]]></wp:meta_value>
  </wp:postmeta>
  <wp:postmeta>
    <wp:meta_key>_irrelevant_key</wp:meta_key>
    <wp:meta_value><![CDATA[irrelevant value]]></wp:meta_value>
  </wp:postmeta>
  <content:encoded><![CDATA[
<span style="font-weight:400;">Example from an early sample post.</span>

<img class="alignnone size-full wp-image-{inline_image_id}" src="https://sitename.files.wordpress.com/2000/01/img_20000101_100000.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!

<img src="https://wordpress.com/images/photo.jpg" />

[gallery ids="{','.join(gallery_image_ids)}" type="rectangular"]

<!-- wp:paragraph -->
<p>Example from later sample post.</p>
<!-- /wp:paragraph -->]]></content:encoded>
</item>
"""


class TestAttachments:
    def test_maps_id_to_url(self, attachment_data: str) -> None:
        source = io.StringIO(rss_doc(attachment_data))

        attachments = wp.attachments_by_id(source)

        assert attachment_id in attachments
        assert attachments[attachment_id] == attachment_url


class TestPosts:
    def test_iterates_over_published_posts(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source))

        assert post.title == 'Post title'

    def test_post_knows_its_name(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source))

        assert post.slug == 'post-name'

    def test_post_knows_its_tags(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source, [], [wp.tag_parser]))

        assert post.tags == ['tag-1', 'tag-2']

    def test_post_knows_thumbnail_attachment_id(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))
        url = 'https://site/path/image.jpg'
        attachments = {thumbnail_id: url}
        parser = wp.thumbnail_parser(attachments)

        post = next(wp.posts(source, [], [parser]))

        assert post.thumbnail == url

    def test_post_knows_its_html_content(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source))

        assert 'Example from an early sample post.' in post.content
        assert 'Example from later sample post.' in post.content

    def test_hosted_images_are_identified(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        attachments = {
            '123': 'https://site/path/image123.jpg',
            '456': 'https://site/path/image456.jpg',
            '1234': 'https://site/path/image1234.jpg',
        }
        post = next(wp.posts(source, [wp.GalleryFilter(attachments)]))

        assert post.attachment_ids == set(
            [inline_image_id] + gallery_image_ids
        )


class TestDeSpanFilter:
    def test_removes_span_tags_around_paragraph(self) -> None:
        content = """Paragraph 1

<span>Paragraph 2</span>

<img alt="Alt text" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />

<span>Paragraph 3</span>
"""

        text = wp.DeSpanFilter()(content)

        assert 'Paragraph 1\n\nParagraph 2' in text
        assert 'Paragraph 2\n\n<img' in text
        assert 'height="3120" />\n\nParagraph 3' in text


class TestRemoveImageLinksFilter:
    def test_links_to_displayed_image_are_removed(self) -> None:
        image_url = 'http://sitename.files.wordpress.com/image.jpg'
        image_tag = f'<img class="wp-image-1234 alignnone size-full" src="{image_url}" alt="" />'
        content = f'<a href="{image_url}">{image_tag}</a>'

        text = wp.RemoveImageLinksFilter()(content)

        assert text == image_tag


class TestIllustratedParagraphFilter:
    def test_ignores_images_followed_by_a_space(self) -> None:
        content = """
<img src="https://sitename.files.wordpress.com/image.jpg"> Paragraph text
"""

        text = wp.IllustratedParagraphFilter()(content)

        assert '/image.jpg"> Paragraph text' in text

    def test_ignores_inline_images(self) -> None:
        content = 'Inline <img src="image.jpg">is fine'

        text = wp.IllustratedParagraphFilter()(content)

        assert text == content

    def test_inserts_line_after_image_at_start_of_line(self) -> None:
        content = """
<img src="https://sitename.files.wordpress.com/image.jpg">Paragraph text
"""

        text = wp.IllustratedParagraphFilter()(content)

        assert '/image.jpg">\n\nParagraph text' in text


class TestGalleryFilter:
    def img_tag(self, image_id: str, urls: dict[str, str]) -> str:
        url = urls[image_id]
        return f'<img class="wp-image-{image_id}" src="{url}">'

    def test_converts_image_galleries_to_html_image_tags(self) -> None:
        image_1 = '123'
        image_2 = '456'
        urls = {
            image_1: 'https://sitename.files.wordpress.com/2000/01/image1.jpg',
            image_2: 'https://sitename.files.wordpress.com/2000/01/image2.jpg',
        }

        gallery_filter = wp.GalleryFilter(urls)
        html = gallery_filter(
            f'[gallery ids="{image_1},{image_2}" type="rectangular"]'
        )

        tag_1 = self.img_tag(image_1, urls)
        tag_2 = self.img_tag(image_2, urls)
        assert '\n\n'.join((tag_1, tag_2)) == html

    def test_ignore_gallery_images_not_included_in_export(self) -> None:
        exported = '123'
        not_exported = '456'
        urls = {
            exported: 'https://sitename.files.wordpress.com/2000/01/image1.jpg'
        }

        gallery_filter = wp.GalleryFilter(urls)
        html = gallery_filter(
            f'[gallery ids="{exported},{not_exported}" type="square"]'
        )

        assert self.img_tag(exported, urls) == html
