import unittest
from unittest.mock import Mock, patch

import requests

from facebook.poster import FacebookPostError, post_to_facebook


class FacebookPosterTests(unittest.TestCase):
    @patch("facebook.poster.requests.post")
    def test_successful_post_returns_id(self, mock_post):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {"id": "page_post"}
        mock_post.return_value = response

        post_id = post_to_facebook("Hello", "page", "token", "v24.0", 15)

        self.assertEqual(post_id, "page_post")
        self.assertEqual(
            mock_post.call_args.args[0],
            "https://graph.facebook.com/v24.0/page/feed",
        )
        self.assertEqual(mock_post.call_args.kwargs["timeout"], 15)
        self.assertEqual(mock_post.call_args.kwargs["data"]["access_token"], "token")

    @patch("facebook.poster.requests.post")
    def test_api_error_is_sanitized_and_raised(self, mock_post):
        response = Mock(ok=False, status_code=400)
        response.json.return_value = {
            "error": {"message": "Invalid token", "code": 190, "type": "OAuthException"}
        }
        mock_post.return_value = response

        with self.assertRaisesRegex(FacebookPostError, "code 190"):
            post_to_facebook("Hello", "page", "secret-token")

    def test_missing_credentials_fail_before_request(self):
        with patch("facebook.poster.requests.post") as mock_post:
            with self.assertRaises(FacebookPostError):
                post_to_facebook("Hello", "", "")
            mock_post.assert_not_called()

    @patch("facebook.poster.requests.post")
    def test_network_error_is_raised(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(FacebookPostError):
            post_to_facebook("Hello", "page", "token")


if __name__ == "__main__":
    unittest.main()
