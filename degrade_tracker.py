"""
Degrade Tracker Module
This module tracks test results history and detects degrade scenarios.

Degrade Rules:
1. Previous version PASS + Current version FAIL = DEGRADE
2. If next version still fails:
   - Different fail reason: Create new issue, mark as degrade
   - Same fail reason: Comment on previous degrade JIRA
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Tuple


# Default history file location
HISTORY_FILE = Path.home() / '.jira_test_history.json'


class DegradeTracker:
    """Track test results and detect degrade scenarios"""
    
    def __init__(self, history_file: Path = HISTORY_FILE):
        """Initialize the degrade tracker
        
        Args:
            history_file: Path to the JSON file storing test history
        """
        self.history_file = history_file
        self.history = self._load_history()
        
    def _load_history(self) -> dict:
        """Load test history from file"""
        if not self.history_file.exists():
            return {}
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'Warning: Failed to load history file: {e}')
            return {}
            
    def _save_history(self):
        """Save test history to file"""
        try:
            # Ensure parent directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f'Warning: Failed to save history file: {e}')
            
    def _get_test_key(self, test_info: dict) -> str:
        """Generate a unique key for a test case
        
        Args:
            test_info: Test information dictionary
            
        Returns:
            Unique key combining IC, model, test case name
        """
        ti = test_info.get('TestInformation', {})
        ic_name = ti.get('chipset', 'UNKNOWN')
        model = ti.get('Model', 'UNKNOWN')
        test_case = ti.get('TestcaseName', 'UNKNOWN')
        
        return f"{ic_name}_{model}_{test_case}"
        
    def _get_fail_reason_hash(self, test_info: dict) -> str:
        """Generate a hash of the fail reason to compare failures
        
        We use the 'Detail' field from FailLog as the fail reason.
        
        Args:
            test_info: Test information dictionary
            
        Returns:
            Hash string of the fail reason
        """
        fail_log = test_info.get('FailLog', {})
        detail = fail_log.get('Detail', '')
        
        # Normalize the detail string (remove extra whitespace, lowercase)
        normalized = ' '.join(detail.split()).lower()
        
        # Create hash
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
        
    def _extract_version_number(self, version_str: str) -> int:
        """Extract numeric version from version string
        
        Args:
            version_str: Version string (e.g., 'DB2188', '808')
            
        Returns:
            Integer version number
        """
        # Remove non-numeric prefix
        numeric_part = ''.join(c for c in version_str if c.isdigit())
        return int(numeric_part) if numeric_part else 0
        
    def check_degrade(self, test_info: dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if current test represents a degrade scenario
        
        Args:
            test_info: Current test information
            
        Returns:
            Tuple of (is_degrade, action, existing_jira_key)
            - is_degrade: True if this is a degrade scenario
            - action: 'create_new' or 'comment_existing' or None
            - existing_jira_key: JIRA key to comment on (if action is 'comment_existing')
        """
        ti = test_info.get('TestInformation', {})
        test_key = self._get_test_key(test_info)
        current_version = ti.get('ImageVersion', '')
        current_db = ti.get('DailyBuildNumber', '')
        current_fail_hash = self._get_fail_reason_hash(test_info)
        
        # Get test history
        test_history = self.history.get(test_key, {})
        
        if not test_history:
            # First time seeing this test - not a degrade
            return False, None, None
            
        last_result = test_history.get('last_result')
        last_version = test_history.get('last_version', '')
        last_db = test_history.get('last_db', '')
        
        # Check if this is a degrade (previous PASS, current FAIL)
        if last_result == 'PASS':
            # This is a degrade!
            print(f'DEGRADE detected: {test_key} was PASS in {last_version}/{last_db}, now FAIL in {current_version}/{current_db}')
            return True, 'create_new', None
            
        elif last_result == 'FAIL':
            # Was already failing, check if fail reason is same or different
            last_fail_hash = test_history.get('last_fail_hash', '')
            last_jira_key = test_history.get('last_jira_key', '')
            
            if current_fail_hash == last_fail_hash:
                # Same fail reason - comment on existing JIRA
                print(f'Same failure detected: {test_key} still failing with same reason in {current_version}/{current_db}')
                if last_jira_key:
                    return True, 'comment_existing', last_jira_key
                else:
                    # No existing JIRA to comment on, treat as new degrade
                    return True, 'create_new', None
            else:
                # Different fail reason - create new issue but still mark as degrade
                print(f'Different failure detected: {test_key} failing with different reason in {current_version}/{current_db}')
                return True, 'create_new', None
        
        return False, None, None
        
    def record_test_result(self, test_info: dict, result: str, jira_key: str = None):
        """Record a test result in history
        
        Args:
            test_info: Test information dictionary
            result: 'PASS' or 'FAIL'
            jira_key: JIRA issue key (if created)
        """
        ti = test_info.get('TestInformation', {})
        test_key = self._get_test_key(test_info)
        version = ti.get('ImageVersion', '')
        db = ti.get('DailyBuildNumber', '')
        
        record = {
            'last_result': result,
            'last_version': version,
            'last_db': db,
            'last_updated': ti.get('JenkinsURL', '')
        }
        
        if result == 'FAIL':
            record['last_fail_hash'] = self._get_fail_reason_hash(test_info)
            if jira_key:
                record['last_jira_key'] = jira_key
                
        self.history[test_key] = record
        self._save_history()
        
    def get_comment_text(self, test_info: dict) -> str:
        """Generate comment text for existing JIRA issue
        
        Args:
            test_info: Current test information
            
        Returns:
            Comment text in JIRA markup format
        """
        ti = test_info.get('TestInformation', {})
        version = ti.get('ImageVersion', '')
        db = ti.get('DailyBuildNumber', '')
        jenkins_url = ti.get('JenkinsURL', '')
        log_path = ti.get('LogPath', '')
        
        fail_log = test_info.get('FailLog', {})
        fail_detail = fail_log.get('Detail', '')
        
        comment_lines = [
            f'*Still failing in version {version} (Daily Build: {db})*',
            '',
            'h4. Test Information',
            f'* Image Version: {version}',
            f'* Daily Build Number: {db}',
            f'* Jenkins URL: {jenkins_url}',
            f'* Log Path: {log_path}',
            '',
            'h4. Fail Log',
            '{code:java}',
            fail_detail,
            '{code}'
        ]
        
        return '\n'.join(comment_lines)
