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
  <category domain="post_tag" nicename="tag-1"><![CDATA[tag 1]]></category>
  <category domain="post_tag" nicename="tag-2"><![CDATA[tag 2]]></category>
  <category domain="category" nicename="uncategorized"><![CDATA[Uncategorized]]></category>
  <content:encoded><![CDATA[
<span style="font-weight:400;">Example from an early sample post.</span>

<img class="alignnone size-full wp-image-1234" src="https://sitename.files.wordpress.com/2000/01/img_20000101_100000.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!

<!-- wp:paragraph -->
<p>Example from later sample post.</p>
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


def test_post_knows_its_tags() -> None:
    source = io.StringIO(rss_doc(post_data))

    post = next(wp.posts(source))

    assert post.tags == ['tag-1', 'tag-2']


def test_post_knows_its_html_content() -> None:
    source = io.StringIO(rss_doc(post_data))

    post = next(wp.posts(source))

    assert 'Example from an early sample post.' in post.content
    assert 'Example from later sample post.' in post.content
