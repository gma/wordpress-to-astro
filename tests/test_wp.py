import io

from .context import wp
from .context import rss_doc


post_data = """
<item>
  <title><![CDATA[Post title]]></title>
  <pubDate>Tue, 24 Oct 2023 15:25:27 +0000</pubDate>
  <wp:post_date_gmt>2023-10-24 15:25:27</wp:post_date_gmt>
  <wp:post_name>post-name</wp:post_name>
  <wp:post_type>post</wp:post_type>
  <wp:status>publish</wp:status>
  <content:encoded><![CDATA[<!-- wp:paragraph -->
<p>This is a sample post.</p>
<!-- /wp:paragraph -->]]></content:encoded>
</item>
"""


def test_iterates_over_published_posts() -> None:
    source = io.StringIO(rss_doc(post_data))

    post = next(wp.posts(source))

    assert post.title == 'Post title'


def test_post_knows_its_name() -> None:
    source = io.StringIO(rss_doc(post_data))

    post = next(wp.posts(source))

    assert post.slug == 'post-name'


def test_post_knows_its_html_content() -> None:
    source = io.StringIO(rss_doc(post_data))

    post = next(wp.posts(source))

    assert '<p>This is a sample post.</p>' in post.content