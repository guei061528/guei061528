"""
Example usage of the email formatter for test reports
"""

import tempfile
import os
from email_formatter import (
    EmailFormatter, 
    TestInfo, 
    TestCase, 
    Patch,
    create_email_report
)


def example_basic_usage():
    """Example of basic usage"""
    
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
        name="test_database_connection",
        status="FAILED",
        detail="Connection timeout after 30 seconds. Database server may be unreachable.",
        performance_value=None
    ))
    
    formatter.add_failed_testcase(TestCase(
        name="test_api_response_time",
        status="FAILED",
        detail="Response time exceeded threshold. Expected < 200ms, got 450ms.",
        performance_value=450.0,
        performance_unit="ms"
    ))
    
    formatter.add_failed_testcase(TestCase(
        name="test_memory_usage",
        status="FAILED",
        detail="Memory consumption exceeded limit during stress test.",
        performance_value=2048.5,
        performance_unit="MB"
    ))
    
    # Add failed patches
    formatter.add_failed_patch(Patch(
        link="https://github.com/example/repo/pull/1234",
        owner="john.doe",
        title="Fix authentication issue in login module"
    ))
    
    formatter.add_failed_patch(Patch(
        link="https://github.com/example/repo/pull/1235",
        owner="jane.smith",
        title="Update database schema migration"
    ))
    
    # Add skipped patches
    formatter.add_skipped_patch(Patch(
        link="https://github.com/example/repo/pull/1236",
        owner="bob.wilson",
        title="Add new feature for user preferences",
        skip_reason="Conflicts with pending changes in main branch"
    ))
    
    formatter.add_skipped_patch(Patch(
        link="https://github.com/example/repo/pull/1237",
        owner="alice.johnson",
        title="Refactor logging module",
        skip_reason="Waiting for dependency update to complete"
    ))
    
    # Add pending patches
    formatter.add_pending_patch(Patch(
        link="https://github.com/example/repo/pull/1238",
        owner="charlie.brown",
        title="Optimize query performance"
    ))
    
    formatter.add_pending_patch(Patch(
        link="https://github.com/example/repo/pull/1239",
        owner="david.lee",
        title="Add caching layer for API responses"
    ))
    
    # Generate HTML email
    html_email = formatter.format_html()
    
    # Save to file for preview
    html_path = os.path.join(tempfile.gettempdir(), "test_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_email)
    print(f"HTML email saved to {html_path}")
    
    # Generate plain text email
    text_email = formatter.format_plain_text()
    
    # Save to file for preview
    text_path = os.path.join(tempfile.gettempdir(), "test_report.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_email)
    print(f"Plain text email saved to {text_path}")
    
    return html_email, text_email


def example_convenience_function():
    """Example using the convenience function"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v2.0.0",
        platform="Windows 10 x64",
        config="Debug",
        test_plan_name="Integration Tests",
        fail_count=5,
        total_count=200
    )
    
    failed_testcases = [
        TestCase(
            name="test_file_upload",
            status="FAILED",
            detail="File upload failed with 500 Internal Server Error"
        ),
        TestCase(
            name="test_throughput",
            status="FAILED",
            detail="Throughput below expected baseline",
            performance_value=850.0,
            performance_unit="req/s"
        )
    ]
    
    failed_patches = [
        Patch(
            link="https://github.com/example/repo/pull/2001",
            owner="developer1",
            title="Fix file handling in upload service"
        )
    ]
    
    skipped_patches = [
        Patch(
            link="https://github.com/example/repo/pull/2002",
            owner="developer2",
            title="Update configuration parser",
            skip_reason="Missing required test coverage"
        )
    ]
    
    pending_patches = [
        Patch(
            link="https://github.com/example/repo/pull/2003",
            owner="developer3",
            title="Add retry mechanism for network requests"
        )
    ]
    
    # Create HTML report
    html_report = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="html"
    )
    
    # Create text report
    text_report = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="text"
    )
    
    return html_report, text_report


def example_minimal_usage():
    """Example with minimal data (only test info, no failures)"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v1.0.0",
        platform="macOS ARM64",
        config="Release",
        test_plan_name="Smoke Tests",
        fail_count=0,
        total_count=50
    )
    
    formatter = EmailFormatter(test_info)
    
    html_email = formatter.format_html()
    text_email = formatter.format_plain_text()
    
    return html_email, text_email


if __name__ == "__main__":
    print("=" * 80)
    print("Email Formatter - Example Usage")
    print("=" * 80)
    print()
    
    # Run basic example
    print("Running basic example...")
    html, text = example_basic_usage()
    print()
    print("Plain text preview (first 500 characters):")
    print("-" * 80)
    print(text[:500])
    print("...")
    print()
    
    # Run convenience function example
    print("Running convenience function example...")
    html2, text2 = example_convenience_function()
    print("Created reports using convenience function")
    print()
    
    # Run minimal example
    print("Running minimal example (all tests passed)...")
    html3, text3 = example_minimal_usage()
    print("Created minimal report")
    print()
    
    print("=" * 80)
    print("Examples completed successfully!")
    temp_dir = tempfile.gettempdir()
    print(f"Check {temp_dir}/test_report.html and {temp_dir}/test_report.txt for output")
    print("=" * 80)
