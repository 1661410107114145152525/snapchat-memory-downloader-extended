# Security

## URL Validation

This application implements strict URL validation to protect against security vulnerabilities.

### Security Issue Addressed

**Problem**: The application downloads media files from URLs specified in the `memories_history.json` file. Without validation, a malicious actor could modify this JSON file to include URLs pointing to:
- Malware or malicious content
- Internal network resources (SSRF attacks)
- Data exfiltration endpoints
- Any arbitrary domain

**Solution**: We now validate that all download URLs point to trusted Snapchat domains only.

### Trusted Domains

The following domains are trusted for downloads:
- `snapchat.com` (and all subdomains like `cdn.snapchat.com`)
- `sc-cdn.net` (and all subdomains)
- `snap-dev.net` (and all subdomains)
- `snapkit.co` (and all subdomains)

### Validation Rules

The URL validation function (`is_trusted_url()`) enforces the following security rules:

1. **HTTPS Only**: Only `https` scheme is allowed (no unencrypted HTTP for security)
2. **Domain Matching**: The hostname must exactly match or be a subdomain of a trusted domain
3. **No Internal IPs**: Requests to localhost, 127.0.0.1, or private IP ranges are explicitly blocked (SSRF protection)
4. **Case-Insensitive**: Domain matching is case-insensitive for security
5. **Complete Validation**: Malformed URLs are rejected

### Examples

✅ **Allowed URLs:**
```
https://snapchat.com/media/file.jpg
https://cdn.snapchat.com/media/file.mp4
https://static.sc-cdn.net/media/file.jpg
https://media.snap-dev.net/file.mp4
```

❌ **Blocked URLs:**
```
https://evil.com/malware.exe
https://attacker.com/steal-data.jpg
https://localhost/admin
https://192.168.1.1/internal
http://snapchat.com/file.jpg  (HTTP not allowed, only HTTPS)
ftp://snapchat.com/file.jpg
https://snapchat.com.evil.com/file.jpg
```

### Error Messages

When an invalid URL is detected, the application will:
1. Skip downloading the file
2. Display a security warning: `✗ SECURITY: Untrusted URL detected, skipping for safety`
3. Show the rejected URL
4. Count it as an error in the final statistics

### Testing

The security feature is covered by comprehensive tests:
- `test_url_validation.py`: Unit tests for the URL validation function
- `test_integration.py`: Integration tests verifying the validation works in the download flow

Run tests with:
```bash
python -m unittest test_url_validation.py -v
python -m unittest test_integration.py -v
```

### Recommendations

1. **Verify JSON Source**: Only use `memories_history.json` files from official Snapchat data exports
2. **Review URLs**: If you see security warnings, review your JSON file for suspicious URLs
3. **Report Issues**: If legitimate Snapchat URLs are being blocked, please open an issue with the URL
4. **Keep Updated**: Keep the application updated to ensure you have the latest security fixes

## Reporting Security Issues

If you discover a security vulnerability in this application, please report it by opening a GitHub issue. Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Note**: For legitimate Snapchat domains that are incorrectly blocked, please open a regular issue with the domain name.
