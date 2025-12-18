# JIRA Auto-Creation System with Degrade Mechanism

This system automatically creates JIRA issues for test failures and includes intelligent degrade detection.

## Features

### 1. Automatic JIRA Creation
- Creates JIRA sub-tasks from JSON test information
- Uploads test logs and video files as attachments
- Sets appropriate assignees, watchers, and labels
- Handles flaky tests by routing to infrastructure team

### 2. Degrade Detection Mechanism

The system tracks test results across versions and detects "degrade" scenarios where tests go from PASS to FAIL.

#### Degrade Rules:

1. **Initial Degrade**: When a test that passed in the previous version fails in the current version:
   - Creates a new JIRA issue
   - Adds `[DEGRADE]` marker to the title
   - Adds `degrade` label
   - Records the failure in history

2. **Continued Failure - Same Reason**: When a test continues to fail with the same error:
   - **Does NOT** create a new JIRA issue
   - Adds a comment to the existing degrade JIRA
   - Includes new version info and logs in the comment
   - Updates history with latest failure

3. **Continued Failure - Different Reason**: When a test continues to fail but with a different error:
   - Creates a new JIRA issue
   - Adds `[DEGRADE]` marker to the title
   - Adds `degrade` label
   - Records the new failure in history

## Files

- `jira_create.py` - Main script for creating JIRA issues
- `degrade_tracker.py` - Module for tracking test history and detecting degrades
- `JIRABase.py` - Stub interface for JIRA API operations
- `test_degrade.py` - Test suite for degrade mechanism

## Usage

### Basic Usage

```bash
python jira_create.py \
  --project MA \
  --parent MA-1234 \
  --json test_results.json
```

### With Credentials

```bash
python jira_create.py \
  --account your.email@company.com \
  --password your_password \
  --project MA \
  --parent MA-1234 \
  --json test_results.json
```

### Programmatic API

```python
from jira_create import create_subtask_from_json

issue_key = create_subtask_from_json(
    json_path='test_results.json',
    project='MA',
    parent='MA-1234'
)
print(f'Created/Updated: {issue_key}')
```

## Test Information JSON Format

```json
{
  "TestInformation": {
    "chipset": "MacArthur7P",
    "Model": "DEMETER",
    "TestcaseName": "test_ccc_11_21_str_dtv",
    "TestLabel": "DC off/on (STR)",
    "ImageVersion": "808",
    "DailyBuildNumber": "DB2188",
    "Country": "Germany",
    "ProjectID": "35",
    "DeviceSet": "run_patron_set6",
    "JenkinsURL": "http://jenkins.example.com/job/test/123/",
    "LogPath": "/path/to/logs",
    "LocalLogPath": "/local/path/to/logs"
  },
  "FailLog": {
    "Value": "Failed",
    "Detail": "[scaler] MISSING 'RTK Disable Main ForceBG': Failed to disable Main ForceBG."
  },
  "ExpectedResult": "Test should pass",
  "Problem": "Main ForceBG not disabled"
}
```

## History Tracking

Test results are tracked in `~/.jira_test_history.json`:

```json
{
  "MacArthur7P_DEMETER_test_ccc_11_21_str_dtv": {
    "last_result": "FAIL",
    "last_version": "808",
    "last_db": "DB2188",
    "last_fail_hash": "abc123...",
    "last_jira_key": "MA-12345",
    "last_updated": "http://jenkins.example.com/job/test/123/"
  }
}
```

## Degrade Detection Logic

The system uses the following key to identify unique tests:

```
{IC_NAME}_{MODEL}_{TEST_CASE_NAME}
```

Example: `MacArthur7P_DEMETER_test_ccc_11_21_str_dtv`

Failure reasons are compared using MD5 hash of the normalized `FailLog.Detail` field.

## Examples

### Scenario 1: First Failure (Degrade)

**Version 807**: Test PASS  
**Version 808**: Test FAIL

→ Creates JIRA: `[DEGRADE][MacArthur7P][DB2188][DEMETER][808] test_ccc_11_21_str_dtv - ...`  
→ Adds label: `degrade`

### Scenario 2: Same Failure Continues

**Version 808**: Test FAIL (JIRA MA-12345 created)  
**Version 809**: Test FAIL (same error)

→ Adds comment to MA-12345:  
```
*Still failing in version 809 (Daily Build: DB2189)*

Test Information
* Image Version: 809
* Daily Build Number: DB2189
...

Fail Log
[scaler] MISSING 'RTK Disable Main ForceBG': Failed to disable Main ForceBG.
```

### Scenario 3: Different Failure Continues

**Version 808**: Test FAIL (error A)  
**Version 809**: Test FAIL (error B)

→ Creates new JIRA: `[DEGRADE][MacArthur7P][DB2189][DEMETER][809] test_ccc_11_21_str_dtv - ...`  
→ Adds label: `degrade`

## Configuration

### Flaky Tests

Tests can be marked as flaky in `FLAKY_TESTS` dictionary. These will be routed to the infrastructure team (PATRONDEV project).

### Assignees and Watchers

- **ML projects**: Assigned to stanley.ko
- **MA projects**: Assigned to drizzle_tseng  
- **PATRONDEV projects**: Assigned to chingyu.huang
- Default: kenny_wu

## Notes

- Title is limited to 255 characters
- Description is limited to 32,767 characters
- Attachments include video files and zipped logs
- History is persistent across runs
- Supports authentication via `~/.jirasecret` file

## Testing

Run the test suite:

```bash
python test_degrade.py
```

This will test:
- First failure detection (degrade)
- Same failure continuation (comment)
- Different failure continuation (new degrade)
- History tracking and persistence
