# Email Formatter API Documentation

## Table of Contents
- [Data Classes](#data-classes)
- [EmailFormatter Class](#emailformatter-class)
- [Convenience Functions](#convenience-functions)
- [Integration Functions](#integration-functions)
- [Examples](#examples)

---

## Data Classes

### TestInfo

Represents test execution information.

```python
@dataclass
class TestInfo:
    daily_build_name: str    # Name of the daily build
    platform: str            # Test platform (e.g., "Linux x86_64", "Windows 10")
    config: str              # Build configuration (e.g., "Release", "Debug")
    test_plan_name: str      # Name of the test plan
    fail_count: int          # Number of failed tests
    total_count: int         # Total number of tests executed
```

**Example:**
```python
test_info = TestInfo(
    daily_build_name="DailyBuild_2025-12-09_v1.2.3",
    platform="Linux x86_64",
    config="Release",
    test_plan_name="Regression Test Suite",
    fail_count=5,
    total_count=150
)
```

---

### TestCase

Represents a single test case result.

```python
@dataclass
class TestCase:
    name: str                           # Test case name/identifier
    status: str                         # Test status (e.g., "FAILED", "ERROR")
    detail: str                         # Detailed failure description
    performance_value: Optional[float]  # Performance metric (for perf tests)
    performance_unit: Optional[str]     # Unit of measurement (e.g., "ms", "MB", "req/s")
```

**Example:**
```python
# Regular test case
testcase1 = TestCase(
    name="test_database_connection",
    status="FAILED",
    detail="Connection timeout after 30 seconds",
    performance_value=None,
    performance_unit=None
)

# Performance test case
testcase2 = TestCase(
    name="test_api_response_time",
    status="FAILED",
    detail="Response time exceeded threshold. Expected < 200ms, got 450ms",
    performance_value=450.0,
    performance_unit="ms"
)
```

---

### Patch

Represents a code patch/change.

```python
@dataclass
class Patch:
    link: str                       # URL to patch (e.g., GitHub PR, Gerrit change)
    owner: str                      # Patch owner/author
    title: str                      # Patch title/description
    skip_reason: Optional[str]      # Reason for skipping (only for skipped patches)
```

**Example:**
```python
# Failed patch
failed_patch = Patch(
    link="https://github.com/example/repo/pull/1234",
    owner="john.doe",
    title="Fix authentication issue in login module"
)

# Skipped patch
skipped_patch = Patch(
    link="https://github.com/example/repo/pull/1235",
    owner="jane.smith",
    title="Update database schema migration",
    skip_reason="Conflicts with pending changes in main branch"
)
```

---

## EmailFormatter Class

Main class for formatting test reports.

### Constructor

```python
EmailFormatter(test_info: TestInfo)
```

**Parameters:**
- `test_info`: TestInfo object containing test execution information

**Example:**
```python
formatter = EmailFormatter(test_info)
```

---

### Methods

#### add_failed_testcase

```python
def add_failed_testcase(testcase: TestCase) -> None
```

Add a failed test case to the report.

**Parameters:**
- `testcase`: TestCase object representing the failed test

**Example:**
```python
formatter.add_failed_testcase(TestCase(
    name="test_login",
    status="FAILED",
    detail="Invalid credentials not rejected"
))
```

---

#### add_failed_patch

```python
def add_failed_patch(patch: Patch) -> None
```

Add a patch that caused test failures.

**Parameters:**
- `patch`: Patch object representing the failed patch

**Example:**
```python
formatter.add_failed_patch(Patch(
    link="https://github.com/example/repo/pull/123",
    owner="developer1",
    title="Fix security vulnerability"
))
```

---

#### add_skipped_patch

```python
def add_skipped_patch(patch: Patch) -> None
```

Add a patch that was skipped during testing.

**Parameters:**
- `patch`: Patch object with skip_reason specified

**Example:**
```python
formatter.add_skipped_patch(Patch(
    link="https://github.com/example/repo/pull/124",
    owner="developer2",
    title="Refactor logging module",
    skip_reason="Missing required test coverage"
))
```

---

#### add_pending_patch

```python
def add_pending_patch(patch: Patch) -> None
```

Add a patch that is pending testing.

**Parameters:**
- `patch`: Patch object representing the pending patch

**Example:**
```python
formatter.add_pending_patch(Patch(
    link="https://github.com/example/repo/pull/125",
    owner="developer3",
    title="Optimize query performance"
))
```

---

#### format_html

```python
def format_html() -> str
```

Generate HTML formatted email report.

**Returns:**
- String containing complete HTML email with embedded CSS

**Features:**
- Professional styling with colors
- Responsive tables
- Clickable links
- Color-coded sections
- Pass rate calculation

**Example:**
```python
html_content = formatter.format_html()
```

---

#### format_plain_text

```python
def format_plain_text() -> str
```

Generate plain text formatted email report.

**Returns:**
- String containing plain text email

**Features:**
- Clean, readable format
- Structured sections with separators
- Numbered lists
- Compatible with all email clients

**Example:**
```python
text_content = formatter.format_plain_text()
```

---

## Convenience Functions

### create_email_report

```python
def create_email_report(
    test_info: TestInfo,
    failed_testcases: List[TestCase] = None,
    failed_patches: List[Patch] = None,
    skipped_patches: List[Patch] = None,
    pending_patches: List[Patch] = None,
    format_type: str = "html"
) -> str
```

Convenience function to create an email report in one call.

**Parameters:**
- `test_info`: TestInfo object
- `failed_testcases`: List of failed TestCase objects (optional)
- `failed_patches`: List of failed Patch objects (optional)
- `skipped_patches`: List of skipped Patch objects (optional)
- `pending_patches`: List of pending Patch objects (optional)
- `format_type`: "html" or "text" (default: "html")

**Returns:**
- Formatted email content as string

**Example:**
```python
html_report = create_email_report(
    test_info=test_info,
    failed_testcases=[testcase1, testcase2],
    failed_patches=[patch1],
    skipped_patches=[patch2],
    pending_patches=[patch3, patch4],
    format_type="html"
)
```

---

## Integration Functions

See `email_integration.py` for email sending functions.

### send_email_smtp

```python
def send_email_smtp(
    subject: str,
    html_content: str,
    text_content: str,
    sender: str,
    recipients: List[str],
    smtp_server: str,
    smtp_port: int = 587,
    username: str = None,
    password: str = None
) -> bool
```

Send email using SMTP protocol.

**Parameters:**
- `subject`: Email subject line
- `html_content`: HTML formatted email body
- `text_content`: Plain text email body (fallback)
- `sender`: Sender email address
- `recipients`: List of recipient email addresses
- `smtp_server`: SMTP server address
- `smtp_port`: SMTP server port (default: 587)
- `username`: SMTP authentication username (optional)
- `password`: SMTP authentication password (optional)

**Returns:**
- `True` if email sent successfully, `False` otherwise

---

### send_test_report_email

```python
def send_test_report_email(
    test_info: TestInfo,
    failed_testcases: List[TestCase] = None,
    failed_patches: List[Patch] = None,
    skipped_patches: List[Patch] = None,
    pending_patches: List[Patch] = None,
    recipients: List[str] = None,
    smtp_config: dict = None
) -> bool
```

Generate and send test report email in one call.

**Parameters:**
- `test_info`: TestInfo object
- `failed_testcases`: List of failed test cases
- `failed_patches`: List of failed patches
- `skipped_patches`: List of skipped patches
- `pending_patches`: List of pending patches
- `recipients`: List of email recipients
- `smtp_config`: SMTP configuration dictionary

**SMTP Config Dictionary:**
```python
smtp_config = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'sender': 'test-automation@example.com'
}
```

**Returns:**
- `True` if email sent successfully, `False` otherwise

---

## Examples

### Example 1: Basic Usage

```python
from email_formatter import EmailFormatter, TestInfo, TestCase, Patch

# Create test info
test_info = TestInfo(
    daily_build_name="DailyBuild_2025-12-09",
    platform="Linux x86_64",
    config="Release",
    test_plan_name="Smoke Tests",
    fail_count=1,
    total_count=50
)

# Create formatter
formatter = EmailFormatter(test_info)

# Add data
formatter.add_failed_testcase(TestCase(
    name="test_startup",
    status="FAILED",
    detail="Application crashed on startup"
))

# Generate email
html = formatter.format_html()
text = formatter.format_plain_text()
```

---

### Example 2: Performance Test Report

```python
from email_formatter import create_email_report, TestInfo, TestCase

test_info = TestInfo(
    daily_build_name="PerformanceTest_2025-12-09",
    platform="Linux x86_64",
    config="Release",
    test_plan_name="Performance Regression Tests",
    fail_count=2,
    total_count=25
)

failed_tests = [
    TestCase(
        name="test_api_latency",
        status="FAILED",
        detail="95th percentile latency exceeded threshold",
        performance_value=285.5,
        performance_unit="ms"
    ),
    TestCase(
        name="test_throughput",
        status="FAILED",
        detail="Throughput below baseline",
        performance_value=850.0,
        performance_unit="req/s"
    )
]

html_report = create_email_report(
    test_info=test_info,
    failed_testcases=failed_tests,
    format_type="html"
)
```

---

### Example 3: Complete Report with All Sections

```python
from email_formatter import EmailFormatter, TestInfo, TestCase, Patch

# Setup
test_info = TestInfo(
    daily_build_name="DailyBuild_2025-12-09_v2.1.0",
    platform="Windows 10 x64",
    config="Debug",
    test_plan_name="Full Regression Suite",
    fail_count=5,
    total_count=200
)

formatter = EmailFormatter(test_info)

# Add failed tests
formatter.add_failed_testcase(TestCase(
    name="test_memory_leak",
    status="FAILED",
    detail="Memory usage increased by 50% over 1 hour",
    performance_value=1024.5,
    performance_unit="MB"
))

# Add failed patches
formatter.add_failed_patch(Patch(
    link="https://github.com/org/repo/pull/101",
    owner="dev1",
    title="Implement new caching mechanism"
))

# Add skipped patches
formatter.add_skipped_patch(Patch(
    link="https://github.com/org/repo/pull/102",
    owner="dev2",
    title="Update dependencies",
    skip_reason="Conflicts with PR #101"
))

# Add pending patches
formatter.add_pending_patch(Patch(
    link="https://github.com/org/repo/pull/103",
    owner="dev3",
    title="Fix security issue"
))

# Generate reports
html = formatter.format_html()
text = formatter.format_plain_text()
```

---

## Email Subject Line Format

When sending automated emails, use consistent subject line format:

```
[PASSED/FAILED] Test Report - {build_name} - {test_plan}
```

Examples:
- `[PASSED] Test Report - DailyBuild_2025-12-09_v1.0 - Smoke Tests`
- `[FAILED] Test Report - DailyBuild_2025-12-09_v1.0 - Regression Suite`

---

## Best Practices

1. **Always provide test information**: TestInfo is required for all reports
2. **Include performance values**: For performance tests, always include value and unit
3. **Provide detailed failure descriptions**: Help developers quickly understand issues
4. **Specify skip reasons**: Always explain why patches were skipped
5. **Use both HTML and text**: Provide both formats for email compatibility
6. **Consistent naming**: Use consistent formats for build names, platforms, etc.

---

## Return Values Summary

| Method/Function | Return Type | Description |
|----------------|-------------|-------------|
| `format_html()` | `str` | Complete HTML email with CSS |
| `format_plain_text()` | `str` | Plain text formatted email |
| `create_email_report()` | `str` | HTML or text based on format_type |
| `send_email_smtp()` | `bool` | True if sent successfully |
| `send_test_report_email()` | `bool` | True if sent successfully |

---

## Requirements

- Python 3.7+ (for dataclasses)
- No external dependencies for formatting
- `smtplib` (built-in) for email sending
