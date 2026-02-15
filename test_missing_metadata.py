"""
Test suite for handling missing metadata (GPS) in videos and images.

Ensures that date/time metadata is still set even when GPS data is missing.
"""

import unittest
from unittest.mock import MagicMock, patch, call
from main import set_metadata, verify_metadata


class TestSetMetadataWithMissingGPS(unittest.TestCase):
    """Test that set_metadata handles missing GPS gracefully"""

    def setUp(self):
        self.mock_et = MagicMock()
        self.date = '2024:01:15 12:00:00'

    def test_video_with_gps_sets_all_tags(self):
        """Video with GPS should set both date and GPS tags"""
        result = set_metadata('/tmp/test.mp4', self.date, '37.7749', '-122.4194', 'video', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_called_once()
        tags = self.mock_et.set_tags.call_args[1]['tags']
        # Should have date tags
        self.assertIn('CreateDate', tags)
        self.assertIn('TrackCreateDate', tags)
        self.assertIn('MediaCreateDate', tags)
        # Should have GPS tags
        self.assertIn('QuickTime:GPSCoordinates', tags)
        self.assertIn('XMP:GPSLatitude', tags)

    def test_video_without_gps_sets_date_only(self):
        """Video without GPS should still set date tags"""
        result = set_metadata('/tmp/test.mp4', self.date, None, None, 'video', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_called_once()
        tags = self.mock_et.set_tags.call_args[1]['tags']
        # Should have date tags
        self.assertIn('CreateDate', tags)
        self.assertIn('TrackCreateDate', tags)
        self.assertIn('TrackModifyDate', tags)
        self.assertIn('MediaCreateDate', tags)
        self.assertIn('MediaModifyDate', tags)
        # Should NOT have GPS tags
        self.assertNotIn('QuickTime:GPSCoordinates', tags)
        self.assertNotIn('XMP:GPSLatitude', tags)
        self.assertNotIn('XMP:GPSLongitude', tags)

    def test_video_with_empty_string_gps_sets_date_only(self):
        """Video with empty string GPS should still set date tags"""
        result = set_metadata('/tmp/test.mp4', self.date, '', '', 'video', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_called_once()
        tags = self.mock_et.set_tags.call_args[1]['tags']
        self.assertIn('CreateDate', tags)
        self.assertNotIn('QuickTime:GPSCoordinates', tags)

    def test_image_with_gps_sets_all_tags(self):
        """Image with GPS should set both date and GPS tags"""
        result = set_metadata('/tmp/test.jpg', self.date, '37.7749', '-122.4194', 'image', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_called_once()
        tags = self.mock_et.set_tags.call_args[1]['tags']
        # Should have date tags
        self.assertIn('DateTimeOriginal', tags)
        self.assertIn('CreateDate', tags)
        self.assertIn('OffsetTimeOriginal', tags)
        # Should have GPS tags
        self.assertIn('GPSLatitude', tags)
        self.assertIn('GPSLongitude', tags)

    def test_image_without_gps_sets_date_only(self):
        """Image without GPS should still set date tags"""
        result = set_metadata('/tmp/test.jpg', self.date, None, None, 'image', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_called_once()
        tags = self.mock_et.set_tags.call_args[1]['tags']
        # Should have date tags
        self.assertIn('DateTimeOriginal', tags)
        self.assertIn('CreateDate', tags)
        self.assertIn('OffsetTimeOriginal', tags)
        self.assertIn('OffsetTime', tags)
        # Should NOT have GPS tags
        self.assertNotIn('GPSLatitude', tags)
        self.assertNotIn('GPSLongitude', tags)

    def test_png_skips_metadata(self):
        """PNG files should skip metadata entirely"""
        result = set_metadata('/tmp/test.png', self.date, '37.7749', '-122.4194', 'image', self.mock_et)
        self.assertTrue(result)
        self.mock_et.set_tags.assert_not_called()

    def test_mov_without_gps_sets_date_by_extension(self):
        """MOV file without GPS should still set video date tags based on extension"""
        result = set_metadata('/tmp/test.mov', self.date, None, None, 'image', self.mock_et)
        self.assertTrue(result)
        tags = self.mock_et.set_tags.call_args[1]['tags']
        # Should use video tags due to .mov extension
        self.assertIn('TrackCreateDate', tags)
        self.assertIn('MediaCreateDate', tags)


class TestVerifyMetadataWithMissingGPS(unittest.TestCase):
    """Test that verify_metadata handles missing GPS gracefully"""

    def setUp(self):
        self.mock_et = MagicMock()
        self.date = '2024:01:15 12:00:00'

    def test_verify_video_without_gps_checks_date(self):
        """Verification of video without GPS should check date tags"""
        self.mock_et.get_metadata.return_value = [{'CreateDate': '2024:01:15 13:00:00'}]
        result = verify_metadata('/tmp/test.mp4', self.date, None, None, 'video', self.mock_et)
        self.assertTrue(result)

    def test_verify_image_without_gps_checks_date(self):
        """Verification of image without GPS should check date tags"""
        self.mock_et.get_metadata.return_value = [{'DateTimeOriginal': '2024:01:15 13:00:00'}]
        result = verify_metadata('/tmp/test.jpg', self.date, None, None, 'image', self.mock_et)
        self.assertTrue(result)

    def test_verify_video_without_gps_no_metadata_still_passes(self):
        """Verification of video without GPS and no date metadata should still pass"""
        self.mock_et.get_metadata.return_value = [{}]
        result = verify_metadata('/tmp/test.mp4', self.date, None, None, 'video', self.mock_et)
        self.assertTrue(result)

    def test_verify_video_with_gps_checks_gps(self):
        """Verification of video with GPS should check GPS tags"""
        self.mock_et.get_metadata.return_value = [{'QuickTime:GPSCoordinates': '37.7749, 122.4194'}]
        result = verify_metadata('/tmp/test.mp4', self.date, '37.7749', '-122.4194', 'video', self.mock_et)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
