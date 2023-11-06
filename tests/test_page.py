from .context import page


def test_content_parser_records_ids_of_images_with_wp_image_class() -> None:
    image_id = '1234'
    content = f"""
<img class="alignnone size-full wp-image-{image_id}" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!
"""

    parser = page.ContentParser()
    parser.feed(content)
    parser.close()

    assert parser.attachment_ids == [image_id]


def test_content_parser_finds_ids_of_gallery_images() -> None:
    image_1 = '123'
    image_2 = '456'
    image_3 = '789'
    content = f"""
[gallery ids="{image_1}" type="rectangular"]

[gallery ids="{image_2},{image_3}" type="rectangular"]
"""

    post = page.Page('Title', 'slug', '2023-10-30', [], content)

    assert post.attachment_ids == [image_1, image_2, image_3]


def test_page_can_list_hosted_attachment_ids() -> None:
    image_id = '1234'
    content = f"""
<img class="alignnone size-full wp-image-{image_id}" src="https://sitename.files.wordpress.com/2000/01/image.jpg" alt="Alt text" width="4160" height="3120" />Paragraph content follows immediately!
"""

    post = page.Page('Title', 'slug', '2023-10-30', [], content)

    assert post.attachment_ids == [image_id]
