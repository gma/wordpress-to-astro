import io

from .context import wp
from .context import rss_doc


post_data = """
<item>
  <title><![CDATA[Post title]]></title>
  <pubDate>Tue, 24 Oct 2023 15:25:27 +0000</pubDate>
  <wp:post_name>post-name</wp:post_name>
  <wp:post_type>post</wp:post_type>
  <wp:status>publish</wp:status>
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
