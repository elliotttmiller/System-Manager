"""
Unit tests for ConfigManager
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from core.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(Path(self.test_dir))
        self.config_manager.initialize()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test configuration initialization."""
        self.assertTrue(self.config_manager.config_file.exists())
        self.assertTrue(self.config_manager.profiles_file.exists())
    
    def test_load_config(self):
        """Test loading configuration."""
        config = self.config_manager.load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('settings', config)
        self.assertIn('security', config)
    
    def test_add_profile(self):
        """Test adding device profile."""
        profile = {
            'hostname': '192.168.1.100',
            'username': 'testuser',
            'port': 22,
        }
        self.config_manager.add_profile('test-server', profile)
        
        retrieved = self.config_manager.get_profile('test-server')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['hostname'], '192.168.1.100')
    
    def test_delete_profile(self):
        """Test deleting device profile."""
        profile = {'hostname': 'test.com', 'username': 'user'}
        self.config_manager.add_profile('test', profile)
        
        self.assertTrue(self.config_manager.delete_profile('test'))
        self.assertIsNone(self.config_manager.get_profile('test'))
    
    def test_list_profiles(self):
        """Test listing profiles."""
        profiles = self.config_manager.list_profiles()
        self.assertIsInstance(profiles, list)
        
        self.config_manager.add_profile('server1', {'hostname': 'host1'})
        self.config_manager.add_profile('server2', {'hostname': 'host2'})
        
        profiles = self.config_manager.list_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertIn('server1', profiles)
        self.assertIn('server2', profiles)
    
    def test_get_setting(self):
        """Test getting configuration setting."""
        value = self.config_manager.get_setting('settings.auto_reconnect')
        self.assertIsInstance(value, bool)
    
    def test_set_setting(self):
        """Test setting configuration value."""
        self.config_manager.set_setting('settings.auto_reconnect', False)
        value = self.config_manager.get_setting('settings.auto_reconnect')
        self.assertFalse(value)


if __name__ == '__main__':
    unittest.main()
