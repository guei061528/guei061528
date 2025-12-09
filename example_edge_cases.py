"""
Example demonstrating edge cases for email formatter:
1. Build failure scenario (image cannot be built)
2. No patches scenario (no patches available for testing)
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


def example_build_failure():
    """Example when image build fails"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v2.0.0",
        platform="Linux x86_64",
        config="Release",
        test_plan_name="Regression Test Suite",
        fail_count=0,
        total_count=0,
        build_error="Docker image build failed: Error during layer creation - insufficient disk space (available: 2.5GB, required: 5GB)"
    )
    
    formatter = EmailFormatter(test_info)
    
    # No test results or patches because build failed
    
    html_email = formatter.format_html()
    text_email = formatter.format_plain_text()
    
    # Save to file for preview
    html_path = os.path.join(tempfile.gettempdir(), "build_failure_report.html")
    text_path = os.path.join(tempfile.gettempdir(), "build_failure_report.txt")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_email)
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_email)
    
    print(f"Build failure example saved to:")
    print(f"  HTML: {html_path}")
    print(f"  Text: {text_path}")
    
    return html_email, text_email


def example_no_patches():
    """Example when no patches are available"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v2.1.0",
        platform="Windows 10 x64",
        config="Debug",
        test_plan_name="Integration Tests",
        fail_count=0,
        total_count=0,
        no_patches_reason="No new patches submitted in the past 24 hours. Repository synchronization completed successfully but found no changes."
    )
    
    formatter = EmailFormatter(test_info)
    
    # No patches to test
    
    html_email = formatter.format_html()
    text_email = formatter.format_plain_text()
    
    # Save to file for preview
    html_path = os.path.join(tempfile.gettempdir(), "no_patches_report.html")
    text_path = os.path.join(tempfile.gettempdir(), "no_patches_report.txt")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_email)
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_email)
    
    print(f"No patches example saved to:")
    print(f"  HTML: {html_path}")
    print(f"  Text: {text_path}")
    
    return html_email, text_email


def example_both_issues():
    """Example with both build error and no patches"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v3.0.0",
        platform="macOS ARM64",
        config="Release",
        test_plan_name="Smoke Tests",
        fail_count=0,
        total_count=0,
        build_error="Build timeout after 30 minutes - dependency download failed",
        no_patches_reason="Patch repository unreachable - network timeout"
    )
    
    formatter = EmailFormatter(test_info)
    
    html_email = formatter.format_html()
    text_email = formatter.format_plain_text()
    
    # Save to file for preview
    html_path = os.path.join(tempfile.gettempdir(), "both_issues_report.html")
    text_path = os.path.join(tempfile.gettempdir(), "both_issues_report.txt")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_email)
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_email)
    
    print(f"Both issues example saved to:")
    print(f"  HTML: {html_path}")
    print(f"  Text: {text_path}")
    
    return html_email, text_email


def example_partial_success():
    """Example with patches but build issues for some tests"""
    
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v3.5.0",
        platform="Linux x86_64",
        config="Release",
        test_plan_name="Full Test Suite",
        fail_count=1,
        total_count=50,
        build_error="Warning: Some optional components failed to build (video codec module)"
    )
    
    formatter = EmailFormatter(test_info)
    
    # Add some test results
    formatter.add_failed_testcase(TestCase(
        name="test_video_encoding",
        status="FAILED",
        detail="Video encoding test skipped due to missing codec module",
        performance_value=None
    ))
    
    # Add patches
    formatter.add_skipped_patch(Patch(
        link="https://github.com/example/repo/pull/301",
        owner="video.team",
        title="Optimize video encoding pipeline",
        skip_reason="Cannot test - video codec module build failed"
    ))
    
    formatter.add_pending_patch(Patch(
        link="https://github.com/example/repo/pull/302",
        owner="core.team",
        title="Update core library dependencies"
    ))
    
    html_email = formatter.format_html()
    text_email = formatter.format_plain_text()
    
    # Save to file for preview
    html_path = os.path.join(tempfile.gettempdir(), "partial_success_report.html")
    text_path = os.path.join(tempfile.gettempdir(), "partial_success_report.txt")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_email)
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_email)
    
    print(f"Partial success example saved to:")
    print(f"  HTML: {html_path}")
    print(f"  Text: {text_path}")
    
    return html_email, text_email


if __name__ == "__main__":
    print("=" * 80)
    print("Edge Cases Examples - Email Formatter")
    print("=" * 80)
    print()
    
    print("1. Build Failure Scenario")
    print("-" * 80)
    example_build_failure()
    print()
    
    print("2. No Patches Scenario")
    print("-" * 80)
    example_no_patches()
    print()
    
    print("3. Both Issues Scenario")
    print("-" * 80)
    example_both_issues()
    print()
    
    print("4. Partial Success with Warnings")
    print("-" * 80)
    example_partial_success()
    print()
    
    print("=" * 80)
    print("All edge case examples completed!")
    print("=" * 80)
