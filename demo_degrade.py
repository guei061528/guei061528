#!/usr/bin/env python
"""
Demonstration script for degrade mechanism
This script simulates the degrade detection workflow
"""

import sys
import json
from pathlib import Path
from degrade_tracker import DegradeTracker


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def simulate_scenario():
    """Simulate a complete degrade scenario"""
    
    # Use a temporary history file for demo
    demo_history = Path('/tmp/demo_degrade_history.json')
    if demo_history.exists():
        demo_history.unlink()
    
    tracker = DegradeTracker(demo_history)
    
    print_header("Scenario 1: First time test fails (Version 807 PASS → Version 808 FAIL)")
    
    # Simulate version 807 passing
    test_v807 = {
        'TestInformation': {
            'chipset': 'MacArthur7P',
            'Model': 'DEMETER',
            'TestcaseName': 'test_ccc_11_21_str_dtv',
            'ImageVersion': '807',
            'DailyBuildNumber': 'DB2187',
            'JenkinsURL': 'http://jenkins/807/'
        },
        'FailLog': {'Detail': 'N/A'}
    }
    
    print("Recording: Version 807 - PASS")
    tracker.record_test_result(test_v807, 'PASS')
    print("✓ History updated")
    
    # Simulate version 808 failing
    test_v808 = {
        'TestInformation': {
            'chipset': 'MacArthur7P',
            'Model': 'DEMETER',
            'TestcaseName': 'test_ccc_11_21_str_dtv',
            'ImageVersion': '808',
            'DailyBuildNumber': 'DB2188',
            'JenkinsURL': 'http://jenkins/808/'
        },
        'FailLog': {
            'Detail': '[scaler] MISSING \'RTK Disable Main ForceBG\': Failed to disable Main ForceBG.'
        }
    }
    
    print("\nChecking: Version 808 - FAIL")
    is_degrade, action, jira_key = tracker.check_degrade(test_v808)
    
    print(f"  Is Degrade: {is_degrade}")
    print(f"  Action: {action}")
    print(f"  Result: CREATE NEW JIRA with [DEGRADE] marker and 'degrade' label")
    
    tracker.record_test_result(test_v808, 'FAIL', 'MA-12345')
    print("✓ Created JIRA: MA-12345")
    
    print_header("Scenario 2: Same failure continues (Version 809 FAIL - same error)")
    
    # Simulate version 809 failing with same error
    test_v809 = {
        'TestInformation': {
            'chipset': 'MacArthur7P',
            'Model': 'DEMETER',
            'TestcaseName': 'test_ccc_11_21_str_dtv',
            'ImageVersion': '809',
            'DailyBuildNumber': 'DB2189',
            'JenkinsURL': 'http://jenkins/809/'
        },
        'FailLog': {
            'Detail': '[scaler] MISSING \'RTK Disable Main ForceBG\': Failed to disable Main ForceBG.'
        }
    }
    
    print("Checking: Version 809 - FAIL (same error)")
    is_degrade, action, jira_key = tracker.check_degrade(test_v809)
    
    print(f"  Is Degrade: {is_degrade}")
    print(f"  Action: {action}")
    print(f"  Existing JIRA: {jira_key}")
    print(f"  Result: ADD COMMENT to existing JIRA {jira_key}")
    
    comment = tracker.get_comment_text(test_v809)
    print("\n  Comment preview:")
    print("  " + "-" * 76)
    for line in comment.split('\n')[:8]:
        print(f"  {line}")
    print("  ...")
    print("  " + "-" * 76)
    
    tracker.record_test_result(test_v809, 'FAIL', jira_key)
    print("✓ Comment added to MA-12345")
    
    print_header("Scenario 3: Different failure (Version 810 FAIL - different error)")
    
    # Simulate version 810 failing with different error
    test_v810 = {
        'TestInformation': {
            'chipset': 'MacArthur7P',
            'Model': 'DEMETER',
            'TestcaseName': 'test_ccc_11_21_str_dtv',
            'ImageVersion': '810',
            'DailyBuildNumber': 'DB2190',
            'JenkinsURL': 'http://jenkins/810/'
        },
        'FailLog': {
            'Detail': '[video] Timeout waiting for video signal: No signal detected after 30 seconds.'
        }
    }
    
    print("Checking: Version 810 - FAIL (different error)")
    is_degrade, action, jira_key = tracker.check_degrade(test_v810)
    
    print(f"  Is Degrade: {is_degrade}")
    print(f"  Action: {action}")
    print(f"  Result: CREATE NEW JIRA with [DEGRADE] marker and 'degrade' label")
    
    tracker.record_test_result(test_v810, 'FAIL', 'MA-12346')
    print("✓ Created JIRA: MA-12346")
    
    print_header("Summary")
    print("✓ Version 807 (PASS) → Version 808 (FAIL): Created MA-12345 [DEGRADE]")
    print("✓ Version 809 (FAIL - same): Added comment to MA-12345")
    print("✓ Version 810 (FAIL - different): Created MA-12346 [DEGRADE]")
    print("\nHistory file location:", demo_history)
    
    # Show history contents
    print("\nHistory contents:")
    with open(demo_history, 'r') as f:
        history = json.load(f)
    print(json.dumps(history, indent=2))


if __name__ == '__main__':
    try:
        simulate_scenario()
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
