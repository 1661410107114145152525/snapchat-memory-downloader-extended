"""
Integration test for URL validation in the main download flow.

This test creates sample JSON files with valid and invalid URLs
and verifies that the main script correctly accepts/rejects them.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from main import main


class TestURLValidationIntegration(unittest.TestCase):
    """Integration tests for URL validation in main download flow"""

    def setUp(self):
        """Set up temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_json(self, urls):
        """Create a test memories_history.json with given URLs"""
        data = {
            "Saved Media": [
                {
                    "Date": f"2024-01-{str(i+1).zfill(2)} 12:00:00 UTC",
                    "Location": "geo:37.7749,-122.4194",
                    "Media Download Url": url,
                    "Media Type": "IMAGE"
                }
                for i, url in enumerate(urls)
            ]
        }
        with open('memories_history.json', 'w') as f:
            json.dump(data, f)

    @patch('main.exiftool.ExifToolHelper')
    @patch('main.requests.get')
    def test_valid_snapchat_urls_are_processed(self, mock_get, mock_exiftool):
        """Test that valid Snapchat URLs are processed"""
        valid_urls = [
            'https://snapchat.com/media/test1.jpg',
            'https://cdn.snapchat.com/media/test2.jpg',
        ]
        self.create_test_json(valid_urls)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = b'fake image data'
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_get.return_value = mock_response

        # Mock ExifTool
        mock_et_instance = MagicMock()
        mock_exiftool.return_value.__enter__.return_value = mock_et_instance

        # Run main
        main()

        # Verify that requests.get was called for valid URLs
        self.assertEqual(mock_get.call_count, 2)
        call_args = [call[0][0] for call in mock_get.call_args_list]
        self.assertIn(valid_urls[0], call_args)
        self.assertIn(valid_urls[1], call_args)

    @patch('main.exiftool.ExifToolHelper')
    @patch('main.requests.get')
    def test_malicious_urls_are_blocked(self, mock_get, mock_exiftool):
        """Test that malicious URLs are blocked and not processed"""
        malicious_urls = [
            'https://evil.com/malware.exe',
            'https://attacker.com/steal.jpg',
            'http://localhost/admin',
        ]
        self.create_test_json(malicious_urls)

        # Mock ExifTool
        mock_et_instance = MagicMock()
        mock_exiftool.return_value.__enter__.return_value = mock_et_instance

        # Run main
        main()

        # Verify that requests.get was NEVER called for malicious URLs
        mock_get.assert_not_called()

    @patch('main.exiftool.ExifToolHelper')
    @patch('main.requests.get')
    def test_mixed_urls_only_process_valid(self, mock_get, mock_exiftool):
        """Test that with mixed URLs, only valid ones are processed"""
        mixed_urls = [
            'https://snapchat.com/media/valid.jpg',  # Valid
            'https://evil.com/malware.exe',  # Invalid
            'https://cdn.sc-cdn.net/media/valid2.jpg',  # Valid
            'http://localhost/admin',  # Invalid
        ]
        self.create_test_json(mixed_urls)

        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = b'fake image data'
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_get.return_value = mock_response

        # Mock ExifTool
        mock_et_instance = MagicMock()
        mock_exiftool.return_value.__enter__.return_value = mock_et_instance

        # Run main
        main()

        # Verify that requests.get was called only for valid URLs
        self.assertEqual(mock_get.call_count, 2)
        call_args = [call[0][0] for call in mock_get.call_args_list]
        self.assertIn(mixed_urls[0], call_args)  # Valid URL 1
        self.assertIn(mixed_urls[2], call_args)  # Valid URL 2
        self.assertNotIn(mixed_urls[1], call_args)  # Invalid URL 1
        self.assertNotIn(mixed_urls[3], call_args)  # Invalid URL 2


if __name__ == '__main__':
    unittest.main(verbosity=2)
