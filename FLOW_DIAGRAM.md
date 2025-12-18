# Degrade Mechanism Flow Diagram

## Overall System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Test Execution Complete                       │
│                  (JSON test result generated)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              jira_create.py --json test_result.json              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Load test information                           │
│              Check if flaky test → route to PATRONDEV            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Initialize DegradeTracker                           │
│         Load history from ~/.jira_test_history.json              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Check Degrade: tracker.check_degrade()              │
│                                                                   │
│  Test Key: {IC_NAME}_{MODEL}_{TEST_CASE_NAME}                   │
│  Fail Hash: MD5(normalized FailLog.Detail)                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
    ┌──────────────┐              ┌──────────────────┐
    │ No History   │              │  Has History     │
    │ Found        │              │                  │
    └──────┬───────┘              └────────┬─────────┘
           │                               │
           │                     ┌─────────┴──────────┐
           │                     │                    │
           │                     ▼                    ▼
           │            ┌────────────────┐   ┌───────────────┐
           │            │  Last: PASS    │   │  Last: FAIL   │
           │            └───────┬────────┘   └───────┬───────┘
           │                    │                    │
           │                    ▼                    │
           │         ┌──────────────────┐            │
           │         │   is_degrade ✓   │            │
           │         │ action: create   │            │
           │         └──────────────────┘            │
           │                                         │
           │                    ┌────────────────────┴────────────────┐
           │                    │                                     │
           │                    ▼                                     ▼
           │         ┌─────────────────────┐             ┌─────────────────────┐
           │         │ Same fail reason?   │             │Different fail reason│
           │         │ (hash comparison)   │             │                     │
           │         └──────────┬──────────┘             └──────────┬──────────┘
           │                    │                                   │
           │           ┌────────┴─────────┐                         │
           │           │                  │                         │
           │           ▼                  ▼                         ▼
           │    ┌──────────┐      ┌──────────────┐      ┌──────────────────┐
           │    │   YES    │      │      NO      │      │  is_degrade ✓    │
           │    └────┬─────┘      └──────┬───────┘      │ action: create   │
           │         │                   │              └──────────────────┘
           │         ▼                   ▼
           │  ┌─────────────┐     ┌─────────────┐
           │  │is_degrade ✓ │     │is_degrade ✗ │
           │  │comment_exist│     │create_new   │
           │  └─────────────┘     └─────────────┘
           │
           ▼
    ┌──────────────┐
    │is_degrade ✗  │
    │action: None  │
    └──────┬───────┘
           │
           └──────────────┬──────────────┬──────────────┐
                          │              │              │
                          ▼              ▼              ▼
              ┌──────────────────┐  ┌─────────────┐  ┌───────────────┐
              │ comment_existing │  │ create_new  │  │   None        │
              │                  │  │             │  │               │
              │ Add comment to   │  │ Create JIRA │  │ Create JIRA   │
              │ existing JIRA:   │  │             │  │ (normal)      │
              │ - Version info   │  │ Title:      │  │               │
              │ - Fail log       │  │ [DEGRADE]...│  │               │
              │ - Jenkins URL    │  │             │  │               │
              │                  │  │ Labels:     │  │               │
              │ Upload files     │  │ + degrade   │  │               │
              └────────┬─────────┘  └──────┬──────┘  └───────┬───────┘
                       │                   │                 │
                       └───────────────────┴─────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  Record Test Result    │
                               │  in History            │
                               │                        │
                               │  Update:               │
                               │  - last_result: FAIL   │
                               │  - last_version        │
                               │  - last_db             │
                               │  - last_fail_hash      │
                               │  - last_jira_key       │
                               └────────────────────────┘
                                           │
                                           ▼
                               ┌────────────────────────┐
                               │  Save History          │
                               │  ~/.jira_test_history  │
                               │         .json          │
                               └────────────────────────┘
```

## Degrade Detection Details

```
┌─────────────────────────────────────────────────────────────────┐
│                    check_degrade() Logic                         │
└─────────────────────────────────────────────────────────────────┘

Input: test_info (current test result)
Output: (is_degrade, action, existing_jira_key)

Step 1: Get test key
├─ Format: {chipset}_{Model}_{TestcaseName}
└─ Example: "MacArthur7P_DEMETER_test_ccc_11_21_str_dtv"

Step 2: Load history for this test key
├─ If no history → (False, None, None)
└─ If has history → continue to Step 3

Step 3: Compare with last result
├─ last_result == "PASS"
│  └─ Current is FAIL → DEGRADE!
│     └─ Return: (True, 'create_new', None)
│
└─ last_result == "FAIL"
   ├─ Calculate current fail hash
   ├─ Compare with last_fail_hash
   │
   ├─ Hashes MATCH (same error)
   │  └─ Return: (True, 'comment_existing', last_jira_key)
   │
   └─ Hashes DIFFERENT (new error)
      └─ Return: (True, 'create_new', None)

Step 4: Fail hash calculation
├─ Input: FailLog.Detail
├─ Normalize: ' '.join(detail.split()).lower()
├─ Hash: MD5(normalized_text)
└─ Example: "a3779704b9cd17a8f677159ef8c1a194"
```

## Example Scenarios

### Scenario A: PASS → FAIL (First Degrade)

```
Version 807           Version 808
┌──────────┐         ┌──────────┐
│  PASS ✓  │   →    │  FAIL ✗  │
└──────────┘         └──────────┘
     │                    │
     │                    ▼
     │         ┌──────────────────────┐
     │         │ CHECK DEGRADE        │
     │         │ last_result: PASS    │
     │         │ current: FAIL        │
     │         │ → is_degrade: TRUE   │
     │         │ → action: create_new │
     │         └──────────┬───────────┘
     │                    │
     │                    ▼
     │         ┌──────────────────────────────┐
     │         │ CREATE JIRA                  │
     │         │ [DEGRADE][MA][DB2188][808]   │
     │         │ Labels: [..., degrade]       │
     │         │ Key: MA-12345                │
     │         └──────────────────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ HISTORY UPDATED              │
│ last_result: PASS → FAIL     │
│ last_jira_key: MA-12345      │
└──────────────────────────────┘
```

### Scenario B: FAIL → FAIL (Same Error)

```
Version 808                  Version 809
┌───────────────┐           ┌───────────────┐
│  FAIL ✗       │     →    │  FAIL ✗       │
│  Error: A     │           │  Error: A     │
│  MA-12345     │           │  (same)       │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ CHECK DEGRADE        │
                         │ last_result: FAIL    │
                         │ hash_match: TRUE     │
                         │ → is_degrade: TRUE   │
                         │ → comment_existing   │
                         │ → jira: MA-12345     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ ADD COMMENT          │
                         │ To: MA-12345         │
                         │ Content:             │
                         │ - Still failing v809 │
                         │ - Fail log           │
                         │ - Jenkins URL        │
                         └──────────────────────┘
```

### Scenario C: FAIL → FAIL (Different Error)

```
Version 809                  Version 810
┌───────────────┐           ┌───────────────┐
│  FAIL ✗       │     →    │  FAIL ✗       │
│  Error: A     │           │  Error: B     │
│  MA-12345     │           │  (different)  │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ CHECK DEGRADE        │
                         │ last_result: FAIL    │
                         │ hash_match: FALSE    │
                         │ → is_degrade: TRUE   │
                         │ → action: create_new │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────────────┐
                         │ CREATE JIRA                  │
                         │ [DEGRADE][MA][DB2189][809]   │
                         │ Labels: [..., degrade]       │
                         │ Key: MA-12346                │
                         └──────────────────────────────┘
```

## Files and Their Roles

```
jira_create.py
├─ Main entry point
├─ Parse command line args
├─ Load test info JSON
├─ Collect attachments
├─ Check flaky tests
├─ Initialize DegradeTracker ←─────┐
├─ Check degrade scenario          │
├─ Create JIRA or comment          │
└─ Upload attachments              │
                                   │
degrade_tracker.py ────────────────┘
├─ DegradeTracker class
├─ check_degrade()
├─ record_test_result()
├─ get_comment_text()
├─ _get_fail_reason_hash()
└─ _load_history() / _save_history()
    │
    ▼
~/.jira_test_history.json
{
  "test_key": {
    "last_result": "FAIL",
    "last_version": "808",
    "last_db": "DB2188",
    "last_fail_hash": "abc123...",
    "last_jira_key": "MA-12345"
  }
}
```

---

**Note**: This diagram shows the complete flow of the degrade mechanism implementation.
