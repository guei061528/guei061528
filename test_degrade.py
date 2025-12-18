"""
Test suite for degrade tracking mechanism
"""

import json
import tempfile
import unittest
from pathlib import Path
from degrade_tracker import DegradeTracker


class TestDegradeTracker(unittest.TestCase):
    """Test cases for DegradeTracker"""
    
    def setUp(self):
        """Create temporary history file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.history_path = Path(self.temp_file.name)
        self.tracker = DegradeTracker(self.history_path)
        
    def tearDown(self):
        """Clean up temporary files"""
        if self.history_path.exists():
            self.history_path.unlink()
            
    def get_test_info(self, version='808', db='DB2188', fail_detail='Error A'):
        """Generate test info dictionary"""
        return {
            'TestInformation': {
                'chipset': 'MacArthur7P',
                'Model': 'DEMETER',
                'TestcaseName': 'test_ccc_11_21_str_dtv',
                'ImageVersion': version,
                'DailyBuildNumber': db,
                'JenkinsURL': f'http://jenkins.example.com/{version}/'
            },
            'FailLog': {
                'Detail': fail_detail
            }
        }
        
    def test_first_failure_no_degrade(self):
        """Test first time seeing a failing test (no history)"""
        test_info = self.get_test_info()
        
        is_degrade, action, jira_key = self.tracker.check_degrade(test_info)
        
        self.assertFalse(is_degrade)
        self.assertIsNone(action)
        self.assertIsNone(jira_key)
        
    def test_pass_to_fail_is_degrade(self):
        """Test PASS -> FAIL transition (degrade scenario)"""
        test_info = self.get_test_info()
        
        # Record a PASS
        self.tracker.record_test_result(test_info, 'PASS')
        
        # Now check with a FAIL
        is_degrade, action, jira_key = self.tracker.check_degrade(test_info)
        
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'create_new')
        self.assertIsNone(jira_key)
        
    def test_fail_to_fail_same_reason(self):
        """Test FAIL -> FAIL with same error (comment scenario)"""
        test_info_v1 = self.get_test_info(version='808', fail_detail='Error A')
        test_info_v2 = self.get_test_info(version='809', fail_detail='Error A')
        
        # Record first failure
        self.tracker.record_test_result(test_info_v1, 'FAIL', 'MA-12345')
        
        # Check second failure with same error
        is_degrade, action, jira_key = self.tracker.check_degrade(test_info_v2)
        
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'comment_existing')
        self.assertEqual(jira_key, 'MA-12345')
        
    def test_fail_to_fail_different_reason(self):
        """Test FAIL -> FAIL with different error (new degrade scenario)"""
        test_info_v1 = self.get_test_info(version='808', fail_detail='Error A')
        test_info_v2 = self.get_test_info(version='809', fail_detail='Error B - different')
        
        # Record first failure
        self.tracker.record_test_result(test_info_v1, 'FAIL', 'MA-12345')
        
        # Check second failure with different error
        is_degrade, action, jira_key = self.tracker.check_degrade(test_info_v2)
        
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'create_new')
        self.assertIsNone(jira_key)
        
    def test_history_persistence(self):
        """Test that history is persisted across tracker instances"""
        test_info = self.get_test_info()
        
        # Record with first tracker
        self.tracker.record_test_result(test_info, 'FAIL', 'MA-12345')
        
        # Create new tracker instance with same file
        new_tracker = DegradeTracker(self.history_path)
        
        # Check that history was loaded
        test_key = new_tracker._get_test_key(test_info)
        self.assertIn(test_key, new_tracker.history)
        self.assertEqual(new_tracker.history[test_key]['last_result'], 'FAIL')
        self.assertEqual(new_tracker.history[test_key]['last_jira_key'], 'MA-12345')
        
    def test_get_test_key(self):
        """Test test key generation"""
        test_info = self.get_test_info()
        key = self.tracker._get_test_key(test_info)
        
        self.assertEqual(key, 'MacArthur7P_DEMETER_test_ccc_11_21_str_dtv')
        
    def test_fail_reason_hash_normalization(self):
        """Test that fail reason hashing normalizes whitespace"""
        test_info_1 = self.get_test_info(fail_detail='Error   with   spaces')
        test_info_2 = self.get_test_info(fail_detail='Error with spaces')
        
        hash_1 = self.tracker._get_fail_reason_hash(test_info_1)
        hash_2 = self.tracker._get_fail_reason_hash(test_info_2)
        
        # Should be same after normalization
        self.assertEqual(hash_1, hash_2)
        
    def test_fail_reason_hash_case_insensitive(self):
        """Test that fail reason hashing is case insensitive"""
        test_info_1 = self.get_test_info(fail_detail='ERROR MESSAGE')
        test_info_2 = self.get_test_info(fail_detail='error message')
        
        hash_1 = self.tracker._get_fail_reason_hash(test_info_1)
        hash_2 = self.tracker._get_fail_reason_hash(test_info_2)
        
        # Should be same (case insensitive)
        self.assertEqual(hash_1, hash_2)
        
    def test_get_comment_text(self):
        """Test comment text generation"""
        test_info = self.get_test_info(
            version='809',
            db='DB2189',
            fail_detail='[scaler] MISSING RTK Disable Main ForceBG'
        )
        
        comment = self.tracker.get_comment_text(test_info)
        
        # Check that comment contains key information
        self.assertIn('809', comment)
        self.assertIn('DB2189', comment)
        self.assertIn('[scaler] MISSING RTK Disable Main ForceBG', comment)
        self.assertIn('Still failing', comment)
        
    def test_multiple_tests_tracked_separately(self):
        """Test that different tests are tracked separately"""
        test_info_1 = {
            'TestInformation': {
                'chipset': 'MacArthur7P',
                'Model': 'DEMETER',
                'TestcaseName': 'test_A',
                'ImageVersion': '808',
                'DailyBuildNumber': 'DB2188',
                'JenkinsURL': 'http://jenkins/'
            },
            'FailLog': {'Detail': 'Error A'}
        }
        
        test_info_2 = {
            'TestInformation': {
                'chipset': 'MacArthur7P',
                'Model': 'DEMETER',
                'TestcaseName': 'test_B',
                'ImageVersion': '808',
                'DailyBuildNumber': 'DB2188',
                'JenkinsURL': 'http://jenkins/'
            },
            'FailLog': {'Detail': 'Error B'}
        }
        
        # Record both tests
        self.tracker.record_test_result(test_info_1, 'PASS')
        self.tracker.record_test_result(test_info_2, 'FAIL', 'MA-99999')
        
        # Verify separate tracking
        key_1 = self.tracker._get_test_key(test_info_1)
        key_2 = self.tracker._get_test_key(test_info_2)
        
        self.assertIn(key_1, self.tracker.history)
        self.assertIn(key_2, self.tracker.history)
        self.assertEqual(self.tracker.history[key_1]['last_result'], 'PASS')
        self.assertEqual(self.tracker.history[key_2]['last_result'], 'FAIL')
        

class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for complete workflows"""
    
    def setUp(self):
        """Create temporary history file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.history_path = Path(self.temp_file.name)
        
    def tearDown(self):
        """Clean up temporary files"""
        if self.history_path.exists():
            self.history_path.unlink()
            
    def test_complete_degrade_workflow(self):
        """Test complete workflow: PASS -> FAIL -> FAIL (same) -> FAIL (different)"""
        tracker = DegradeTracker(self.history_path)
        
        base_test_info = {
            'TestInformation': {
                'chipset': 'MacArthur7P',
                'Model': 'DEMETER',
                'TestcaseName': 'test_workflow',
                'ImageVersion': '800',
                'DailyBuildNumber': 'DB2100',
                'JenkinsURL': 'http://jenkins/'
            },
            'FailLog': {'Detail': 'No error'}
        }
        
        # Version 800: PASS
        test_v800 = base_test_info.copy()
        test_v800['TestInformation'] = base_test_info['TestInformation'].copy()
        test_v800['TestInformation']['ImageVersion'] = '800'
        tracker.record_test_result(test_v800, 'PASS')
        
        # Version 801: FAIL (degrade!)
        test_v801 = base_test_info.copy()
        test_v801['TestInformation'] = base_test_info['TestInformation'].copy()
        test_v801['TestInformation']['ImageVersion'] = '801'
        test_v801['FailLog'] = {'Detail': 'Timeout error'}
        
        is_degrade, action, jira_key = tracker.check_degrade(test_v801)
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'create_new')
        
        tracker.record_test_result(test_v801, 'FAIL', 'MA-11111')
        
        # Version 802: FAIL with same error (should comment)
        test_v802 = base_test_info.copy()
        test_v802['TestInformation'] = base_test_info['TestInformation'].copy()
        test_v802['TestInformation']['ImageVersion'] = '802'
        test_v802['FailLog'] = {'Detail': 'Timeout error'}  # Same
        
        is_degrade, action, jira_key = tracker.check_degrade(test_v802)
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'comment_existing')
        self.assertEqual(jira_key, 'MA-11111')
        
        tracker.record_test_result(test_v802, 'FAIL', 'MA-11111')
        
        # Version 803: FAIL with different error (new degrade)
        test_v803 = base_test_info.copy()
        test_v803['TestInformation'] = base_test_info['TestInformation'].copy()
        test_v803['TestInformation']['ImageVersion'] = '803'
        test_v803['FailLog'] = {'Detail': 'Connection refused'}  # Different!
        
        is_degrade, action, jira_key = tracker.check_degrade(test_v803)
        self.assertTrue(is_degrade)
        self.assertEqual(action, 'create_new')
        self.assertIsNone(jira_key)


if __name__ == '__main__':
    unittest.main()
