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


class TestPage:
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
