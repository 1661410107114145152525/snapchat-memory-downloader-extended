"""
Test suite for URL validation security feature.

This test suite ensures that the URL validation function properly:
1. Accepts valid Snapchat URLs
2. Rejects malicious or non-Snapchat URLs
3. Prevents potential security vulnerabilities like SSRF attacks
"""

import unittest
from main import is_trusted_url


class TestURLValidation(unittest.TestCase):
    """Test cases for URL validation security"""

    def test_valid_snapchat_domains(self):
        """Test that valid Snapchat URLs are accepted"""
        valid_urls = [
            'https://snapchat.com/media/file.jpg',
            'https://www.snapchat.com/media/file.jpg',
            'https://cdn.snapchat.com/media/file.mp4',
            'https://media.snapchat.com/v1/file.jpg',
            'https://sc-cdn.net/media/file.jpg',
            'https://static.sc-cdn.net/media/file.jpg',
            'https://snap-dev.net/media/file.jpg',
            'https://test.snap-dev.net/media/file.jpg',
            'https://snapkit.co/media/file.jpg',
            'https://cdn.snapkit.co/media/file.jpg',
            'http://snapchat.com/media/file.jpg',  # http is also allowed
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    is_trusted_url(url),
                    f"Valid Snapchat URL was rejected: {url}"
                )

    def test_reject_malicious_domains(self):
        """Test that malicious/untrusted URLs are rejected"""
        malicious_urls = [
            'https://evil.com/malware.exe',
            'https://attacker.com/steal-data.jpg',
            'https://snapchat.com.evil.com/file.jpg',  # Domain spoofing attempt
            'https://snapchatt.com/file.jpg',  # Typosquatting
            'https://snapchat.co/file.jpg',  # Wrong TLD
            'https://snapchat-cdn.com/file.jpg',  # Similar but different
            'https://not-snapchat.com/file.jpg',
            'https://example.com/file.jpg',
        ]
        
        for url in malicious_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"Malicious URL was accepted: {url}"
                )

    def test_reject_invalid_schemes(self):
        """Test that non-HTTP(S) schemes are rejected"""
        invalid_scheme_urls = [
            'ftp://snapchat.com/file.jpg',
            'file:///etc/passwd',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'ssh://snapchat.com/file.jpg',
            'telnet://snapchat.com:23',
        ]
        
        for url in invalid_scheme_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"Invalid scheme URL was accepted: {url}"
                )

    def test_reject_localhost_and_internal_ips(self):
        """Test that localhost and internal IPs are rejected (SSRF protection)"""
        ssrf_urls = [
            'http://localhost/admin',
            'http://127.0.0.1/admin',
            'http://192.168.1.1/admin',
            'http://10.0.0.1/admin',
            'http://172.16.0.1/admin',
            'http://0.0.0.0/admin',
        ]
        
        for url in ssrf_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"SSRF URL was accepted: {url}"
                )

    def test_reject_empty_and_invalid_urls(self):
        """Test that empty and malformed URLs are rejected"""
        invalid_urls = [
            '',
            None,
            'not-a-url',
            'htp://missing-t.com',
            '://no-scheme.com',
            'https://',
            'https:///',
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"Invalid URL was accepted: {url}"
                )

    def test_reject_url_with_credentials(self):
        """Test that URLs with embedded credentials are rejected"""
        # While these might technically work, they're suspicious
        credential_urls = [
            'https://user:pass@evil.com/file.jpg',
            'https://admin:admin@attacker.com/file.jpg',
        ]
        
        for url in credential_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"URL with credentials was accepted: {url}"
                )

    def test_case_insensitive_domain_matching(self):
        """Test that domain matching is case-insensitive"""
        case_variations = [
            'https://SNAPCHAT.COM/file.jpg',
            'https://Snapchat.Com/file.jpg',
            'https://SnapChat.COM/file.jpg',
            'https://CDN.SNAPCHAT.COM/file.jpg',
        ]
        
        for url in case_variations:
            with self.subTest(url=url):
                self.assertTrue(
                    is_trusted_url(url),
                    f"Case variation was rejected: {url}"
                )

    def test_subdomain_validation(self):
        """Test that subdomains of trusted domains are accepted"""
        subdomain_urls = [
            'https://cdn.snapchat.com/file.jpg',
            'https://media.cdn.snapchat.com/file.jpg',
            'https://deep.nested.subdomain.sc-cdn.net/file.jpg',
        ]
        
        for url in subdomain_urls:
            with self.subTest(url=url):
                self.assertTrue(
                    is_trusted_url(url),
                    f"Valid subdomain was rejected: {url}"
                )

    def test_query_parameters_and_fragments(self):
        """Test that URLs with query parameters and fragments are handled correctly"""
        urls_with_params = [
            'https://snapchat.com/file.jpg?token=abc123',
            'https://snapchat.com/file.jpg?token=abc&version=1',
            'https://snapchat.com/file.jpg#anchor',
            'https://snapchat.com/file.jpg?param=value#anchor',
        ]
        
        for url in urls_with_params:
            with self.subTest(url=url):
                self.assertTrue(
                    is_trusted_url(url),
                    f"URL with parameters/fragment was rejected: {url}"
                )

    def test_path_traversal_attempts(self):
        """Test that path traversal attempts don't bypass validation"""
        # These should still be rejected because the domain is not trusted
        path_traversal_urls = [
            'https://evil.com/../../../snapchat.com/file.jpg',
            'https://evil.com/../../file.jpg',
        ]
        
        for url in path_traversal_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    is_trusted_url(url),
                    f"Path traversal URL was accepted: {url}"
                )


if __name__ == '__main__':
    unittest.main(verbosity=2)
