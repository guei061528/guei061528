import sys
import json
import argparse
import shutil
import zipfile

from pathlib import Path
from datetime import datetime
from datetime import timedelta

from JIRABase import RTKJIRA
from degrade_tracker import DegradeTracker


TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
TMP_DIR = Path(f"tmp_attachments_{TIMESTAMP}")

MAX_TITLE_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 32767

DEFAULT_ASSIGNEE = 'kenny_wu'
DEFAULT_WATCHERS = ['gliance597', 'twliou', 'yikang.law', 'chingyu.huang', 'ivan.wang', 'stanley.ko', 'drizzle_tseng', 'kenny_wu', 'shiuan.wen']
INFRA_WATCHERS = ['gliance597', 'twliou', 'yikang.law', 'chingyu.huang']
VIDEO_FILE_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm']
INFRA_ISSUE_LOG_PATTERNS = [
    "[UI]",
    "Channel scan failed",
    "Channel not found within timeout",
    "Test case result format error",
    "Failed to connect to",
    "Command 'adb -s",
    "wait-for-device"
]
FLAKY_TESTS = {
    "DB2143": [
        "test_ccc_10_06_str_lpm_typec_home",
        "test_ccc_10_07_str_lpm_typec",
        "test_ccc_11_02_str_launcher_time"
    ],
    "DB2188": [
        "test_ccc_11_02_str_launcher_time",
        "test_ccc_0212_auto_tuning_antenna_dtv_brazil",
        "test_ccc_0213_auto_tuning_antenna_atv_brazil",
        "test_ccc_0214_auto_tuning_cable_atv_brazil",
        "test_ccc_0215_cc",
        "test_ccc_0216_ginga",
        "test_ccc_0026_dtv_av"
    ],
    "DB2192": [
        "test_ccc_11_02_str_launcher_time",
        "test_ccc_0212_auto_tuning_antenna_dtv_brazil",
        "test_ccc_0213_auto_tuning_antenna_atv_brazil",
        "test_ccc_0214_auto_tuning_cable_atv_brazil",
        "test_ccc_0215_cc",
        "test_ccc_0216_ginga",
        "test_ccc_0026_dtv_av"
    ],
    "DB2247": [
        "test_ccc_11_02_str_launcher_time",
        "test_ccc_0212_auto_tuning_antenna_dtv_brazil",
        "test_ccc_0213_auto_tuning_antenna_atv_brazil",
        "test_ccc_0214_auto_tuning_cable_atv_brazil",
        "test_ccc_0215_cc",
        "test_ccc_0216_ginga",
        "test_ccc_0026_dtv_av"
    ],
    "DB2334": [
        "test_ccc_10_06_str_lpm_typec_home",
        "test_ccc_10_07_str_lpm_typec",
        "test_ccc_11_02_str_launcher_time"
    ]
}


def ensure_tmp_dir():
    TMP_DIR.mkdir(exist_ok=True)


def load_json(json_path: str) -> dict:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_attachments(test_info: dict) -> dict:

    ensure_tmp_dir()

    allFilesPath = {
        "testcase_files": []
    }

    log_path = test_info['TestInformation'].get('LocalLogPath', None)
    test_name = test_info['TestInformation'].get('TestcaseName', 'testcase')

    if not log_path:
        print('No LocalLogPath found in TestInformation; skipping attachment collection.')
        return allFilesPath

    # Collect video files from log_path
    for f in Path(log_path).rglob('*'):
        if f.is_file() and f.suffix.lower() in VIDEO_FILE_EXTENSIONS:
            try:
                shutil.copy2(f, TMP_DIR / f.name)
                allFilesPath['testcase_files'].append(f.name)
                print(f"Copied video file: {f.name}")
            except Exception as e:
                print(f'Failed to copy video file {f}: {e}', file=sys.stderr)

    if Path(log_path).exists():
        zip_name = f"{test_name}_logs.zip"
        zip_path = TMP_DIR / zip_name
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in Path(log_path).rglob('*'):
                    if f.is_file():
                        # Skip video files and test_output.log
                        if f.suffix.lower() not in VIDEO_FILE_EXTENSIONS:
                            try:
                                rel_path = f.relative_to(Path(log_path))
                                zipf.write(f, arcname=str(rel_path))
                            except ValueError:
                                zipf.write(f, arcname=f.name)
            allFilesPath['testcase_files'].append(zip_name)
            print(f"Created zip file: {zip_name}")
        except Exception as e:
            print(f'Failed to create zip file: {e}', file=sys.stderr)

    return allFilesPath


def build_description(test_info: dict, attachments_map: dict, is_degrade: bool = False):
    """Build JIRA title and description with the requested Test info fields.

    Args:
        test_info: Test information dictionary
        attachments_map: Dictionary of attachment files
        is_degrade: Whether this is a degrade scenario

    Returns: (title, description)
    """
    # Get testcase name and daily build number
    ti = test_info.get('TestInformation') if isinstance(test_info.get('TestInformation'), dict) else test_info
    testcase = ''
    if isinstance(ti, dict):
        testcase = ti.get('SQATestcaseName') or ti.get('TestcaseName') or ''
    else:
        testcase = test_info.get('TestcaseName', '')

    daily_build_number = ti.get('DailyBuildNumber', '') if isinstance(ti, dict) else test_info.get('daily_build_number', '')
    image_version = ti.get('ImageVersion', '') if isinstance(ti, dict) else test_info.get('image_version', '')

    # Get IC Name from chipset
    ic_name = ti.get('chipset', '') if isinstance(ti, dict) else test_info.get('chipset', '')
    model = ti.get('Model', '')

    # Get fail log detail
    fail_log_value = ''
    fail_log = test_info.get('FailLog', {})
    if isinstance(fail_log, dict):
        fail_log_value = fail_log.get('Value', '')
        # Remove newline characters from fail_log_value for title
        fail_log_value = fail_log_value.replace('\n', ' ').replace('\r', '')

    # Get fail log detail
    fail_log_detail = ''
    fail_log = test_info.get('FailLog', {})
    if isinstance(fail_log, dict):
        fail_log_detail = fail_log.get('Detail', '')
        # Remove newline characters from fail_log_detail for title
        fail_log_detail = fail_log_detail.replace('\n', ' ').replace('\r', '')

    # Build title with available fields in order of preference
    title_tag = ""
    if ic_name:
        title_tag += f"[{ic_name}]"
    if daily_build_number:
        title_tag += f"[{daily_build_number}]"
    if model:
        title_tag += f"[{model}]"
    if image_version:
        title_tag += f"[{image_version}]"

    title_test_case_name = testcase or "Test"
    title_description = fail_log_detail or "fail"
    
    # Add degrade marker to title if this is a degrade
    degrade_marker = "[DEGRADE] " if is_degrade else ""
    title = f"{degrade_marker}{title_tag} {title_test_case_name} - {title_description}"

    # Build description
    desc_lines = []
    desc_lines.append('*[Test Information]*')

    def get_ti(field_key, fallback=''):
        if isinstance(ti, dict):
            return ti.get(field_key, fallback)
        return test_info.get(field_key.lower().replace(' ', '_'), fallback)

    desc_lines.append(f"Test Case: {get_ti('TestcaseName', '')}")
    desc_lines.append(f"Test Label: {get_ti('TestLabel', '')}")
    desc_lines.append(f"Country: {get_ti('Country', '')}")
    desc_lines.append(f"Project ID: {get_ti('ProjectID', '')}")
    desc_lines.append(f"RC: {get_ti('RC', '')}")
    desc_lines.append(f"HDCP KEY: {get_ti('HDCP_KEY', '')}")
    desc_lines.append(f"RMCA KEY: {get_ti('RMCA_KEY', '')}")
    desc_lines.append(f"Panel Info: {get_ti('PanelInfo', '')}")
    desc_lines.append(f"Source Device: {get_ti('SourceDevice', '')}")
    desc_lines.append(f"Timing Info: {get_ti('TimingInfo', '')}")
    desc_lines.append(f"Audio Output Device: {get_ti('AudioOutputDevice', '')}")
    desc_lines.append(f"Cable Name: {get_ti('CableName', '')}")

    # Condition: may be list
    cond = get_ti('Condition', '')
    if isinstance(cond, list):
        desc_lines.append('Condition:')
        for c in cond:
            desc_lines.append(f"# {c}")
    else:
        desc_lines.append(f"Condition: {cond}")

    # Add new fields
    desc_lines.append('')
    desc_lines.append(f"Image Version: {get_ti('ImageVersion', '')}")
    desc_lines.append(f"Daily Build Number: {get_ti('DailyBuildNumber', '')}")
    desc_lines.append(f"Device Set: {get_ti('DeviceSet', '')}")
    desc_lines.append(f"Jenkins URL: {get_ti('JenkinsURL', '')}")
    desc_lines.append(f"Log Path: {get_ti('LogPath', '')}")

    desc_lines.append('')
    desc_lines.append('Expected Result:')
    # ExpectedResult may be top-level or under TestInformation
    expected = test_info.get('ExpectedResult') if test_info.get('ExpectedResult') is not None else test_info.get('expected_result', '')
    desc_lines.append(expected or '')
    desc_lines.append('')
    desc_lines.append('Problem:')
    problem = test_info.get('Problem') if test_info.get('Problem') is not None else test_info.get('problem', '')
    desc_lines.append(problem or '')

    # Add fail log information
    desc_lines.append('')
    desc_lines.append('Fail Log:')
    fail_log_value = fail_log.get('Value', '') if isinstance(fail_log, dict) else ''
    fail_log_detail = fail_log.get('Detail', '') if isinstance(fail_log, dict) else ''
    if fail_log_value:
        desc_lines.append(f"Value: {fail_log_value}")
    if fail_log_detail:
        desc_lines.append('{code:java}')
        desc_lines.append(f"Detail: {fail_log_detail}")
        desc_lines.append('{code}')

    desc_lines.append('')
    desc_lines.append('Attached files')
    for f in attachments_map.get('testcase_files', []):
        desc_lines.append(f"- [{f}|^{f}]")

    description = '\n'.join(desc_lines)
    return title, description


def create_sub_task(rtkjira_instance: RTKJIRA, jira_prj: str, jira_parent_task: str, test_info: dict, attachments_map: dict, is_degrade: bool = False):
    """Create a JIRA sub-task
    
    Args:
        rtkjira_instance: RTKJIRA instance
        jira_prj: JIRA project key
        jira_parent_task: Parent JIRA task key
        test_info: Test information dictionary
        attachments_map: Dictionary of attachment files
        is_degrade: Whether this is a degrade scenario
        
    Returns:
        Created JIRA issue object
    """

    # Component: prefer TestInformation.JiraComponent, fallback to top-level component, default to 'System'
    jiraKey = None
    if isinstance(test_info.get('TestInformation'), dict):
        jiraKey = test_info['TestInformation'].get('JiraComponent') or test_info.get('component')
    else:
        jiraKey = test_info.get('component')
    if not jiraKey:
        jiraKey = 'System'
    jiraFreq = 'Always(90-100%)'

    # Determine assignee and watchers
    if isinstance(jira_prj, str) and jira_prj.upper().startswith('ML'):
        jiraIssuer = 'stanley.ko'
        watchers = DEFAULT_WATCHERS
    elif isinstance(jira_prj, str) and jira_prj.upper().startswith('MA'):
        jiraIssuer = 'drizzle_tseng'
        watchers = DEFAULT_WATCHERS
    elif isinstance(jira_prj, str) and jira_prj.upper().startswith('PATRONDEV'):
        jiraIssuer = 'chingyu.huang'
        watchers = INFRA_WATCHERS
    else:
        jiraIssuer = DEFAULT_ASSIGNEE
        watchers = DEFAULT_WATCHERS

    # Priority: prefer top-level JiraPriority, fallback to nested TestInformation, default Critical
    if isinstance(test_info, dict):
        jiraPriority = test_info.get('JiraPriority')
        if not jiraPriority and isinstance(test_info.get('TestInformation'), dict):
            jiraPriority = test_info['TestInformation'].get('JiraPriority')
    else:
        jiraPriority = None
    if not jiraPriority:
        jiraPriority = 'Critical'

    # Labels: start from existing labels, then append TestInformation.JiraLabel if present
    base_labels = test_info.get('labels')
    if not isinstance(base_labels, list):
        base_labels = ["AT", "Patron"]
    extra_label = None
    if isinstance(test_info.get('TestInformation'), dict):
        extra_label = test_info['TestInformation'].get('JiraLabel')
    if isinstance(extra_label, str) and extra_label.strip():
        if extra_label not in base_labels:
            base_labels.append(extra_label)
    
    # Add degrade label if this is a degrade
    if is_degrade and 'degrade' not in base_labels:
        base_labels.append('degrade')
    
    jiraLabels = base_labels

    title, description = build_description(test_info, attachments_map, is_degrade)
    print(f'Create sub task with title: {title}, priority: {jiraPriority}, assign: {jiraIssuer}')

    rtkjira_instance.SetProjectName(projectname=jira_prj)

    # Truncate title to MAX_TITLE_LENGTH characters if needed
    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH]

    # Truncate description to MAX_DESCRIPTION_LENGTH characters if needed
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[:MAX_DESCRIPTION_LENGTH]

    jira_sub_task = rtkjira_instance.Create_Sub_Task(
        parentIssue=jira_parent_task,
        summary=title,
        desc=description,
        comp=jiraKey,
        pri=jiraPriority,
        freq=jiraFreq,
        assign=jiraIssuer,
        labels=jiraLabels,
        env=""
    )

    if not jira_sub_task:
        raise RuntimeError('Failed to create sub-task')

    created_key = getattr(jira_sub_task, "key", "(no-key)")
    print(f'Sub Task {created_key} create success')

    # Set Due Date: today + 6 days (YYYY-MM-DD)
    try:
        due_date = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')
        ok = False
        if hasattr(rtkjira_instance, 'Update_Due_Date'):
            ok = bool(rtkjira_instance.Update_Due_Date(created_key, due_date))
        if ok:
            print(f'Set duedate to {due_date} for {created_key}')
        else:
            print(f'Warning: Unable to set duedate programmatically for {created_key}; please verify JIRA API support.', file=sys.stderr)
    except Exception as e:
        print(f'Failed to set duedate for {created_key}: {e}', file=sys.stderr)

    # Add watchers if any
    if watchers:
        for w in watchers:
            try:
                rtkjira_instance.Add_Watcher(created_key, w)
                print(f'Added watcher {w} to {created_key}')
            except Exception as e:
                print(f'Failed to add watcher {w} to {created_key}: {e}', file=sys.stderr)
    return jira_sub_task


def upload_attachments(rtkjira_instance: RTKJIRA, issue_key: str):
    # upload all files in tmp_attachments
    if not TMP_DIR.exists():
        return
    for f in TMP_DIR.iterdir():
        if f.is_file():
            # Skip test_output.log as it's just for debugging
            if f.name == 'test_output.log':
                continue
            try:
                rtkjira_instance.Upload_Attachment(issue_key, str(f))
                print(f'Uploaded {f.name} to {issue_key}')
            except Exception as e:
                print(f'Failed to upload {f}: {e}', file=sys.stderr)


def cleanup_tmp():
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)


def create_subtask_from_json(json_path: str, project: str, parent: str, account: str = None, password: str = None):
    """Programmatic API to create a JIRA sub-task from a JSON test info file.

    Returns the created issue key on success, or raises on failure.
    """
    # load json
    json_data = load_json(json_path)

    # prepare rtkjira (RTKJIRA will read ~/.jirasecret if account/password not provided)
    rtkjira = RTKJIRA(account, password)

    try:
        attachments_map = collect_attachments(json_data)
        
        # Initialize degrade tracker
        degrade_tracker = DegradeTracker()
        
        # Check for degrade scenario
        is_degrade, action, existing_jira_key = degrade_tracker.check_degrade(json_data)
        
        if action == 'comment_existing' and existing_jira_key:
            # Comment on existing JIRA instead of creating new one
            comment_text = degrade_tracker.get_comment_text(json_data)
            rtkjira.Add_Comment(existing_jira_key, comment_text)
            upload_attachments(rtkjira, existing_jira_key)
            degrade_tracker.record_test_result(json_data, 'FAIL', existing_jira_key)
            return existing_jira_key
        
        # Create new issue
        jira_issue = create_sub_task(
            rtkjira, 
            jira_prj=project, 
            jira_parent_task=parent, 
            test_info=json_data, 
            attachments_map=attachments_map,
            is_degrade=is_degrade
        )
        issue_key = getattr(jira_issue, 'key', jira_issue)
        
        # upload attachments
        upload_attachments(rtkjira, issue_key)
        
        # Record test result in history
        degrade_tracker.record_test_result(json_data, 'FAIL', issue_key)
        
        return issue_key
    finally:
        cleanup_tmp()


def is_flaky_test(test_info: dict) -> bool:

    test_name = test_info['TestInformation']['TestcaseName']
    db_number = test_info['TestInformation']['DailyBuildNumber']

    if test_name in FLAKY_TESTS.get(db_number, []):
        print(f'Test {test_name} in {db_number} is marked as a flaky test.')
        return True

    detail = test_info['FailLog'].get('Detail', '')
    for pattern in INFRA_ISSUE_LOG_PATTERNS:
        if pattern in detail:
            print(f'Test fail log matches infra issue pattern: {pattern}')
            return True

    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account', '-a', help='Jira account that you are going to use.', required=False)
    parser.add_argument('--password', '-p', help='Password of the jira account.', required=False)
    parser.add_argument('--project', '-r', help='JIRA project that you are going to create your task.', required=True)
    parser.add_argument('--parent', '-P', help='Parent JIRA key to attach sub-task to.', required=True)
    parser.add_argument('--json', '-j', help='Path to JSON test info file.', required=True)
    args = parser.parse_args()

    jira_account = args.account
    jira_pwd = args.password
    jira_prj = args.project
    jira_parent = args.parent
    json_path = args.json

    # If ~/.jirasecret exists, RTKJIRA will read token from it. If not, require account/password.
    secret_path = Path.home() / '.jirasecret'
    if not secret_path.exists():
        if not jira_account or not jira_pwd:
            print('No ~/.jirasecret found and account/password not provided. Please provide --account and --password', file=sys.stderr)
            sys.exit(1)

    try:
        test_info = load_json(json_path)
    except Exception as e:
        print(f'Failed to load json: {e}', file=sys.stderr)
        sys.exit(1)

    # create rtkjira instance
    rtkjira = RTKJIRA(jira_account, jira_pwd)

    # Collect attachments into tmp_attachments
    attachments_map = collect_attachments(test_info)

    if is_flaky_test(test_info):
        print('Creating issue under PATRONDEV-35')
        jira_prj = 'PATRONDEV'
        jira_parent = 'PATRONDEV-35'

    # Initialize degrade tracker
    degrade_tracker = DegradeTracker()
    
    # Check for degrade scenario
    is_degrade, action, existing_jira_key = degrade_tracker.check_degrade(test_info)
    
    # Create sub task or comment on existing
    try:
        if action == 'comment_existing' and existing_jira_key:
            # Comment on existing JIRA instead of creating new one
            print(f'Adding comment to existing JIRA: {existing_jira_key}')
            comment_text = degrade_tracker.get_comment_text(test_info)
            
            try:
                rtkjira.Add_Comment(existing_jira_key, comment_text)
                print(f'Successfully added comment to {existing_jira_key}')
                
                # Upload attachments to existing issue
                upload_attachments(rtkjira, existing_jira_key)
                
                # Update history
                degrade_tracker.record_test_result(test_info, 'FAIL', existing_jira_key)
                
                cleanup_tmp()
                sys.exit(0)
                
            except Exception as e:
                print(f'Failed to add comment to {existing_jira_key}: {e}', file=sys.stderr)
                print('Will create new issue instead')
                # Fall through to create new issue
        
        # Create new issue (either first time or different fail reason)
        jira_issue = create_sub_task(
            rtkjira, 
            jira_prj=jira_prj, 
            jira_parent_task=jira_parent, 
            test_info=test_info, 
            attachments_map=attachments_map,
            is_degrade=is_degrade
        )
        issue_key = getattr(jira_issue, 'key', jira_issue)

        # Upload attachments
        upload_attachments(rtkjira, issue_key)

        print(f'Created issue: {issue_key}')
        
        # Record test result in history
        degrade_tracker.record_test_result(test_info, 'FAIL', issue_key)

        cleanup_tmp()

    except Exception as e:
        print(f'[RTK JIRA][Error] Create task: {e}', file=sys.stderr)
        cleanup_tmp()
        sys.exit(1)
