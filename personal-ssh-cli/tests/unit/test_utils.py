"""
Unit tests for utility functions
"""
import unittest
from features.utils import (
    format_bytes,
    format_duration,
    validate_hostname,
    validate_ip,
    get_os_type,
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_format_bytes(self):
        """Test byte formatting."""
        self.assertEqual(format_bytes(0), "0.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.0 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.0 GB")
    
    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(format_duration(30), "30s")
        self.assertEqual(format_duration(90), "2m")
        self.assertEqual(format_duration(3600), "60m")
        self.assertEqual(format_duration(7200), "2h")
    
    def test_validate_hostname(self):
        """Test hostname validation."""
        self.assertTrue(validate_hostname("example.com"))
        self.assertTrue(validate_hostname("sub.example.com"))
        self.assertTrue(validate_hostname("server1"))
        self.assertFalse(validate_hostname(""))
        self.assertFalse(validate_hostname("-invalid"))
    
    def test_validate_ip(self):
        """Test IP address validation."""
        self.assertTrue(validate_ip("192.168.1.1"))
        self.assertTrue(validate_ip("10.0.0.1"))
        self.assertTrue(validate_ip("172.16.0.1"))
        self.assertFalse(validate_ip("256.1.1.1"))
        self.assertFalse(validate_ip("invalid"))
        self.assertFalse(validate_ip(""))
    
    def test_get_os_type(self):
        """Test OS type detection."""
        os_type = get_os_type()
        self.assertIn(os_type, ['windows', 'linux', 'macos'])


if __name__ == '__main__':
    unittest.main()
