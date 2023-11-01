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

        post = next(wp.posts(source))

        assert post.tags == ['tag-1', 'tag-2']

    def test_post_knows_its_html_content(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source))

        assert 'Example from an early sample post.' in post.content
        assert 'Example from later sample post.' in post.content

    def test_hosted_images_are_identified(self, post_data: str) -> None:
        source = io.StringIO(rss_doc(post_data))

        post = next(wp.posts(source))

        assert post.attachment_ids == set(
            [inline_image_id] + gallery_image_ids
        )
