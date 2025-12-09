# Email Formatter for Test Reports

A Python module for formatting test results into professional email reports. Supports both HTML and plain text formats.

## Features

### 5 Key Sections

1. **Test Information**
   - Daily Build name
   - Test platform
   - Test configuration
   - Test plan name
   - Fail count / Total test count

2. **Test Results**
   - List of failed test cases
   - Detailed analysis for each failure
   - Performance values for performance-related tests

3. **Failed Patches**
   - Patch link
   - Patch owner
   - Patch title

4. **Skipped Patches**
   - Patch link
   - Patch owner
   - Patch title
   - Skip reason

5. **Pending Prebuilt Patches**
   - Patches waiting to be tested
   - Automatically scheduled when multiple patches from same repository are detected
   - Tests run sequentially from oldest to newest

## Installation

No external dependencies required. Uses only Python standard library.

```bash
# Simply copy email_formatter.py to your project
cp email_formatter.py /path/to/your/project/
```

## Quick Start

```python
from email_formatter import EmailFormatter, TestInfo, TestCase, Patch

# Create test information
test_info = TestInfo(
    daily_build_name="DailyBuild_2025-12-09_v1.2.3",
    platform="Linux x86_64",
    config="Release",
    test_plan_name="Regression Test Suite",
    fail_count=3,
    total_count=150
)

# Create formatter
formatter = EmailFormatter(test_info)

# Add failed test cases
formatter.add_failed_testcase(TestCase(
    name="test_api_response_time",
    status="FAILED",
    detail="Response time exceeded threshold. Expected < 200ms, got 450ms.",
    performance_value=450.0,
    performance_unit="ms"
))

# Add failed patches
formatter.add_failed_patch(Patch(
    link="https://github.com/example/repo/pull/1234",
    owner="john.doe",
    title="Fix authentication issue in login module"
))

# Generate HTML email
html_email = formatter.format_html()

# Generate plain text email
text_email = formatter.format_plain_text()
```

## Usage

### Data Classes

#### TestInfo
```python
@dataclass
class TestInfo:
    daily_build_name: str      # Name of the daily build
    platform: str              # Test platform (e.g., "Linux x86_64")
    config: str                # Test configuration (e.g., "Release", "Debug")
    test_plan_name: str        # Name of the test plan
    fail_count: int            # Number of failed tests
    total_count: int           # Total number of tests
```

#### TestCase
```python
@dataclass
class TestCase:
    name: str                           # Test case name
    status: str                         # Status (e.g., "FAILED")
    detail: str                         # Detailed failure description
    performance_value: Optional[float]  # Performance metric value (if applicable)
    performance_unit: Optional[str]     # Unit of performance metric (e.g., "ms", "MB")
```

#### Patch
```python
@dataclass
class Patch:
    link: str                        # URL to the patch
    owner: str                       # Patch owner/author
    title: str                       # Patch title/description
    skip_reason: Optional[str]       # Reason for skipping (only for skipped patches)
```

### EmailFormatter Class

#### Methods

```python
# Initialize with test information
formatter = EmailFormatter(test_info)

# Add test results
formatter.add_failed_testcase(testcase)

# Add patch information
formatter.add_failed_patch(patch)
formatter.add_skipped_patch(patch)
formatter.add_pending_patch(patch)

# Generate email content
html_content = formatter.format_html()
text_content = formatter.format_plain_text()
```

### Convenience Function

For simpler usage, use the `create_email_report()` function:

```python
from email_formatter import create_email_report, TestInfo, TestCase, Patch

html_report = create_email_report(
    test_info=test_info,
    failed_testcases=[testcase1, testcase2],
    failed_patches=[patch1, patch2],
    skipped_patches=[patch3],
    pending_patches=[patch4],
    format_type="html"  # or "text"
)
```

## Examples

See `example_usage.py` for comprehensive examples:

```bash
python example_usage.py
```

This will generate:
- `/tmp/test_report.html` - HTML formatted report
- `/tmp/test_report.txt` - Plain text formatted report

### Example Output Structure

#### HTML Format
- Professional styling with colors and formatting
- Responsive tables
- Clickable patch links
- Color-coded sections (red for failures, orange for skipped, blue for pending)
- Pass rate calculation and display

#### Plain Text Format
- Clean, readable text format
- Structured sections with separators
- Numbered lists for easy reference
- Suitable for email clients that don't support HTML

## Use Cases

1. **Automated Testing Systems**
   - Send email reports after daily builds
   - Notify team of test failures

2. **CI/CD Integration**
   - Generate test reports in pipelines
   - Email stakeholders with results

3. **Manual Testing**
   - Format manual test results consistently
   - Create professional test reports

## Customization

### Styling (HTML)

The HTML template includes embedded CSS. You can customize:
- Colors for different sections
- Table styling
- Font sizes and families
- Layout and spacing

Edit the `<style>` section in the `format_html()` method.

### Adding Custom Sections

Extend the `EmailFormatter` class to add custom sections:

```python
class CustomEmailFormatter(EmailFormatter):
    def format_html(self):
        html = super().format_html()
        # Add custom sections
        return html
```

## Best Practices

1. **Performance Values**: Always include performance values for performance-related tests to track regressions
2. **Detailed Failures**: Provide clear, actionable detail messages for failed tests
3. **Skip Reasons**: Always specify why a patch was skipped
4. **Consistent Naming**: Use consistent naming conventions for builds, platforms, and test plans

## Requirements

- Python 3.7 or higher (for dataclasses)
- No external dependencies

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Author

Created for test reporting automation.
