import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from facebook.poster import post_photo_to_facebook


class PhotoPosterTests(unittest.TestCase):
    @patch("facebook.poster.requests.post")
    def test_photo_upload_uses_photos_endpoint_and_caption(self, mock_post):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {"id": "photo-id", "post_id": "page-post"}
        mock_post.return_value = response
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "card.png"
            image.write_bytes(b"fake-png-data")
            post_id = post_photo_to_facebook("Caption", image, "page", "token")

        self.assertEqual(post_id, "page-post")
        self.assertTrue(mock_post.call_args.args[0].endswith("/page/photos"))
        self.assertEqual(mock_post.call_args.kwargs["data"]["caption"], "Caption")
        self.assertEqual(mock_post.call_args.kwargs["files"]["source"][0], "card.png")


if __name__ == "__main__":
    unittest.main()
