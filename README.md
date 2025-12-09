- 👋 Hi, I’m Xiao Guei
- 👀 I’m interested in coding, stock, and fitness.
- 🌱 I’m currently learning ...
- 💞️ I’m looking to collaborate on ...
- 📫 How to reach me ...

## Projects

### Email Formatter for Test Reports

A Python module for formatting automated test results into professional email reports.

**Features:**
- ✅ 5 comprehensive sections: Test Info, Test Results, Failed Patches, Skipped Patches, Pending Patches
- ✅ Supports both HTML and Plain Text formats
- ✅ Performance metrics tracking
- ✅ Professional styling with color coding
- ✅ SMTP integration for automated sending

**Documentation:**
- 📖 [README](EMAIL_FORMATTER_README.md) - Quick start and overview
- 📋 [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- 💻 [Example Usage](example_usage.py) - Working examples
- 📧 [Email Integration](email_integration.py) - SMTP integration guide

**Quick Start:**
```python
from email_formatter import EmailFormatter, TestInfo, TestCase, Patch

# Create test info
test_info = TestInfo(
    daily_build_name="DailyBuild_2025-12-09",
    platform="Linux x86_64",
    config="Release",
    test_plan_name="Regression Tests",
    fail_count=3,
    total_count=150
)

# Create formatter and generate report
formatter = EmailFormatter(test_info)
html_report = formatter.format_html()
```

See [EMAIL_FORMATTER_README.md](EMAIL_FORMATTER_README.md) for full documentation.
