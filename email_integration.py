"""
Email Integration Guide

This file demonstrates how to integrate the email formatter with actual email sending.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from email_formatter import (
    EmailFormatter,
    TestInfo,
    TestCase,
    Patch,
    create_email_report
)


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
):
    """
    Send email using SMTP
    
    Args:
        subject: Email subject
        html_content: HTML formatted email body
        text_content: Plain text email body (fallback)
        sender: Sender email address
        recipients: List of recipient email addresses
        smtp_server: SMTP server address
        smtp_port: SMTP server port (default: 587 for TLS)
        username: SMTP username (if authentication required)
        password: SMTP password (if authentication required)
    """
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    # Attach both plain text and HTML versions
    # Email clients will use HTML if supported, otherwise fall back to text
    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        
        if username and password:
            server.login(username, password)
        
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        
        print(f"Email sent successfully to {', '.join(recipients)}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_test_report_email(
    test_info: TestInfo,
    failed_testcases: List[TestCase] = None,
    failed_patches: List[Patch] = None,
    skipped_patches: List[Patch] = None,
    pending_patches: List[Patch] = None,
    recipients: List[str] = None,
    smtp_config: dict = None
):
    """
    Convenience function to generate and send test report email
    
    Args:
        test_info: Test information
        failed_testcases: List of failed test cases
        failed_patches: List of failed patches
        skipped_patches: List of skipped patches
        pending_patches: List of pending patches
        recipients: List of email recipients
        smtp_config: SMTP configuration dict with keys:
            - server: SMTP server address
            - port: SMTP port (default: 587)
            - username: SMTP username (optional)
            - password: SMTP password (optional)
            - sender: Sender email address
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Generate email content
    html_content = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="html"
    )
    
    text_content = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="text"
    )
    
    # Create subject line
    status = "PASSED" if test_info.fail_count == 0 else "FAILED"
    subject = f"[{status}] Test Report - {test_info.daily_build_name} - {test_info.test_plan_name}"
    
    # Send email
    return send_email_smtp(
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        sender=smtp_config.get('sender', 'test-automation@example.com'),
        recipients=recipients or ['team@example.com'],
        smtp_server=smtp_config.get('server', 'smtp.example.com'),
        smtp_port=smtp_config.get('port', 587),
        username=smtp_config.get('username'),
        password=smtp_config.get('password')
    )


def save_to_file(
    test_info: TestInfo,
    failed_testcases: List[TestCase] = None,
    failed_patches: List[Patch] = None,
    skipped_patches: List[Patch] = None,
    pending_patches: List[Patch] = None,
    output_dir: str = "/tmp"
):
    """
    Save test report to files instead of sending email
    Useful for debugging or archiving
    
    Args:
        test_info: Test information
        failed_testcases: List of failed test cases
        failed_patches: List of failed patches
        skipped_patches: List of skipped patches
        pending_patches: List of pending patches
        output_dir: Directory to save files
    """
    import os
    from datetime import datetime
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate content
    html_content = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="html"
    )
    
    text_content = create_email_report(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        skipped_patches=skipped_patches,
        pending_patches=pending_patches,
        format_type="text"
    )
    
    # Save files
    html_file = os.path.join(output_dir, f"test_report_{timestamp}.html")
    text_file = os.path.join(output_dir, f"test_report_{timestamp}.txt")
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"HTML report saved to: {html_file}")
    print(f"Text report saved to: {text_file}")
    
    return html_file, text_file


# Example usage
if __name__ == "__main__":
    # Create sample test data
    test_info = TestInfo(
        daily_build_name="DailyBuild_2025-12-09_v1.2.3",
        platform="Linux x86_64",
        config="Release",
        test_plan_name="Regression Test Suite",
        fail_count=2,
        total_count=100
    )
    
    failed_testcases = [
        TestCase(
            name="test_performance",
            status="FAILED",
            detail="Performance degradation detected",
            performance_value=350.0,
            performance_unit="ms"
        )
    ]
    
    failed_patches = [
        Patch(
            link="https://github.com/example/repo/pull/1234",
            owner="developer1",
            title="Fix performance issue"
        )
    ]
    
    # Example 1: Save to file (for testing)
    print("Saving test report to files...")
    save_to_file(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches
    )
    
    # Example 2: Send email (commented out - uncomment and configure to use)
    """
    smtp_config = {
        'server': 'smtp.gmail.com',
        'port': 587,
        'username': 'your-email@gmail.com',
        'password': 'your-app-password',
        'sender': 'test-automation@example.com'
    }
    
    send_test_report_email(
        test_info=test_info,
        failed_testcases=failed_testcases,
        failed_patches=failed_patches,
        recipients=['team-lead@example.com', 'developer@example.com'],
        smtp_config=smtp_config
    )
    """
