"""
Email Formatter for Test Reports

This module provides functionality to format test results into email format.
It supports both HTML and plain text formats.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TestInfo:
    """Test information container"""
    daily_build_name: str
    platform: str
    config: str
    test_plan_name: str
    fail_count: int
    total_count: int


@dataclass
class TestCase:
    """Test case result"""
    name: str
    status: str
    detail: str
    performance_value: Optional[float] = None
    performance_unit: Optional[str] = None


@dataclass
class Patch:
    """Patch information"""
    link: str
    owner: str
    title: str
    skip_reason: Optional[str] = None


class EmailFormatter:
    """Formats test results into email format"""
    
    def __init__(self, test_info: TestInfo):
        self.test_info = test_info
        self.failed_testcases: List[TestCase] = []
        self.failed_patches: List[Patch] = []
        self.skipped_patches: List[Patch] = []
        self.pending_patches: List[Patch] = []
    
    def add_failed_testcase(self, testcase: TestCase):
        """Add a failed test case"""
        self.failed_testcases.append(testcase)
    
    def add_failed_patch(self, patch: Patch):
        """Add a failed patch"""
        self.failed_patches.append(patch)
    
    def add_skipped_patch(self, patch: Patch):
        """Add a skipped patch"""
        self.skipped_patches.append(patch)
    
    def add_pending_patch(self, patch: Patch):
        """Add a pending prebuilt patch"""
        self.pending_patches.append(patch)
    
    def format_html(self) -> str:
        """Generate HTML formatted email"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
        }
        .info-section {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info-item {
            margin: 8px 0;
        }
        .info-label {
            font-weight: bold;
            display: inline-block;
            width: 180px;
        }
        .fail-count {
            color: #e74c3c;
            font-weight: bold;
            font-size: 1.1em;
        }
        .pass-count {
            color: #27ae60;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background-color: white;
        }
        th {
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .testcase-name {
            font-weight: bold;
            color: #2980b9;
        }
        .performance-value {
            color: #8e44ad;
            font-weight: bold;
        }
        .patch-link {
            color: #3498db;
            text-decoration: none;
        }
        .patch-link:hover {
            text-decoration: underline;
        }
        .skip-reason {
            color: #e67e22;
            font-style: italic;
        }
        .section-count {
            background-color: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.9em;
            margin-left: 10px;
        }
        .warning-section {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
"""
        
        # Section 1: Test Information
        html += self._format_test_info_html()
        
        # Section 2: Test Results
        if self.failed_testcases:
            html += self._format_test_results_html()
        
        # Section 3: Failed Patches
        if self.failed_patches:
            html += self._format_failed_patches_html()
        
        # Section 4: Skipped Patches
        if self.skipped_patches:
            html += self._format_skipped_patches_html()
        
        # Section 5: Pending Patches
        if self.pending_patches:
            html += self._format_pending_patches_html()
        
        html += """
</body>
</html>
"""
        return html
    
    def _format_test_info_html(self) -> str:
        """Format test information section in HTML"""
        pass_count = self.test_info.total_count - self.test_info.fail_count
        pass_rate = (pass_count / self.test_info.total_count * 100) if self.test_info.total_count > 0 else 0
        
        return f"""
    <h1>Test Report</h1>
    
    <h2>1. Test Information</h2>
    <div class="info-section">
        <div class="info-item">
            <span class="info-label">Daily Build:</span>
            <span>{self.test_info.daily_build_name}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Platform:</span>
            <span>{self.test_info.platform}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Configuration:</span>
            <span>{self.test_info.config}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Test Plan:</span>
            <span>{self.test_info.test_plan_name}</span>
        </div>
        <div class="info-item">
            <span class="info-label">Test Results:</span>
            <span class="fail-count">{self.test_info.fail_count} Failed</span> / 
            <span class="pass-count">{pass_count} Passed</span> / 
            <span>{self.test_info.total_count} Total</span>
            <span style="margin-left: 15px;">({pass_rate:.1f}% Pass Rate)</span>
        </div>
    </div>
"""
    
    def _format_test_results_html(self) -> str:
        """Format test results section in HTML"""
        html = f"""
    <h2>2. Test Results <span class="section-count">{len(self.failed_testcases)} Failed</span></h2>
    <table>
        <thead>
            <tr>
                <th style="width: 30%;">Test Case</th>
                <th style="width: 50%;">Detail</th>
                <th style="width: 20%;">Performance</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for testcase in self.failed_testcases:
            perf_display = ""
            if testcase.performance_value is not None:
                unit = testcase.performance_unit or ""
                perf_display = f'<span class="performance-value">{testcase.performance_value} {unit}</span>'
            else:
                perf_display = "N/A"
            
            html += f"""
            <tr>
                <td class="testcase-name">{testcase.name}</td>
                <td>{testcase.detail}</td>
                <td>{perf_display}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
"""
        return html
    
    def _format_failed_patches_html(self) -> str:
        """Format failed patches section in HTML"""
        html = f"""
    <h2>3. Failed Patches <span class="section-count">{len(self.failed_patches)}</span></h2>
    <table>
        <thead>
            <tr>
                <th style="width: 40%;">Patch Link</th>
                <th style="width: 20%;">Owner</th>
                <th style="width: 40%;">Title</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for patch in self.failed_patches:
            html += f"""
            <tr>
                <td><a href="{patch.link}" class="patch-link">{patch.link}</a></td>
                <td>{patch.owner}</td>
                <td>{patch.title}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
"""
        return html
    
    def _format_skipped_patches_html(self) -> str:
        """Format skipped patches section in HTML"""
        html = f"""
    <h2>4. Skipped Patches <span class="section-count" style="background-color: #f39c12;">{len(self.skipped_patches)}</span></h2>
    <table>
        <thead>
            <tr>
                <th style="width: 30%;">Patch Link</th>
                <th style="width: 15%;">Owner</th>
                <th style="width: 30%;">Title</th>
                <th style="width: 25%;">Skip Reason</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for patch in self.skipped_patches:
            skip_reason = patch.skip_reason or "Not specified"
            html += f"""
            <tr>
                <td><a href="{patch.link}" class="patch-link">{patch.link}</a></td>
                <td>{patch.owner}</td>
                <td>{patch.title}</td>
                <td class="skip-reason">{skip_reason}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
"""
        return html
    
    def _format_pending_patches_html(self) -> str:
        """Format pending prebuilt patches section in HTML"""
        html = f"""
    <h2>5. Pending Prebuilt Patches <span class="section-count" style="background-color: #3498db;">{len(self.pending_patches)}</span></h2>
    <div class="warning-section">
        <strong>Note:</strong> These patches are scheduled to be tested. 
        When multiple patches from the same repository are detected, they are tested sequentially starting from the oldest.
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 40%;">Patch Link</th>
                <th style="width: 20%;">Owner</th>
                <th style="width: 40%;">Title</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for patch in self.pending_patches:
            html += f"""
            <tr>
                <td><a href="{patch.link}" class="patch-link">{patch.link}</a></td>
                <td>{patch.owner}</td>
                <td>{patch.title}</td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
"""
        return html
    
    def format_plain_text(self) -> str:
        """Generate plain text formatted email"""
        text = "=" * 80 + "\n"
        text += "TEST REPORT\n"
        text += "=" * 80 + "\n\n"
        
        # Section 1: Test Information
        text += self._format_test_info_text()
        
        # Section 2: Test Results
        if self.failed_testcases:
            text += self._format_test_results_text()
        
        # Section 3: Failed Patches
        if self.failed_patches:
            text += self._format_failed_patches_text()
        
        # Section 4: Skipped Patches
        if self.skipped_patches:
            text += self._format_skipped_patches_text()
        
        # Section 5: Pending Patches
        if self.pending_patches:
            text += self._format_pending_patches_text()
        
        text += "=" * 80 + "\n"
        return text
    
    def _format_test_info_text(self) -> str:
        """Format test information section in plain text"""
        pass_count = self.test_info.total_count - self.test_info.fail_count
        pass_rate = (pass_count / self.test_info.total_count * 100) if self.test_info.total_count > 0 else 0
        
        return f"""1. TEST INFORMATION
{"-" * 80}
Daily Build:     {self.test_info.daily_build_name}
Platform:        {self.test_info.platform}
Configuration:   {self.test_info.config}
Test Plan:       {self.test_info.test_plan_name}
Test Results:    {self.test_info.fail_count} Failed / {pass_count} Passed / {self.test_info.total_count} Total
Pass Rate:       {pass_rate:.1f}%

"""
    
    def _format_test_results_text(self) -> str:
        """Format test results section in plain text"""
        text = f"""2. TEST RESULTS ({len(self.failed_testcases)} Failed Test Cases)
{"-" * 80}
"""
        
        for i, testcase in enumerate(self.failed_testcases, 1):
            text += f"\n[{i}] {testcase.name}\n"
            text += f"    Status: {testcase.status}\n"
            text += f"    Detail: {testcase.detail}\n"
            if testcase.performance_value is not None:
                unit = testcase.performance_unit or ""
                text += f"    Performance: {testcase.performance_value} {unit}\n"
        
        text += "\n"
        return text
    
    def _format_failed_patches_text(self) -> str:
        """Format failed patches section in plain text"""
        text = f"""3. FAILED PATCHES ({len(self.failed_patches)})
{"-" * 80}
"""
        
        for i, patch in enumerate(self.failed_patches, 1):
            text += f"\n[{i}] {patch.title}\n"
            text += f"    Link:  {patch.link}\n"
            text += f"    Owner: {patch.owner}\n"
        
        text += "\n"
        return text
    
    def _format_skipped_patches_text(self) -> str:
        """Format skipped patches section in plain text"""
        text = f"""4. SKIPPED PATCHES ({len(self.skipped_patches)})
{"-" * 80}
"""
        
        for i, patch in enumerate(self.skipped_patches, 1):
            skip_reason = patch.skip_reason or "Not specified"
            text += f"\n[{i}] {patch.title}\n"
            text += f"    Link:        {patch.link}\n"
            text += f"    Owner:       {patch.owner}\n"
            text += f"    Skip Reason: {skip_reason}\n"
        
        text += "\n"
        return text
    
    def _format_pending_patches_text(self) -> str:
        """Format pending prebuilt patches section in plain text"""
        text = f"""5. PENDING PREBUILT PATCHES ({len(self.pending_patches)})
{"-" * 80}
NOTE: These patches are scheduled to be tested. When multiple patches from the
      same repository are detected, they are tested sequentially starting from
      the oldest.

"""
        
        for i, patch in enumerate(self.pending_patches, 1):
            text += f"\n[{i}] {patch.title}\n"
            text += f"    Link:  {patch.link}\n"
            text += f"    Owner: {patch.owner}\n"
        
        text += "\n"
        return text


def create_email_report(test_info: TestInfo, 
                       failed_testcases: List[TestCase] = None,
                       failed_patches: List[Patch] = None,
                       skipped_patches: List[Patch] = None,
                       pending_patches: List[Patch] = None,
                       format_type: str = "html") -> str:
    """
    Convenience function to create an email report
    
    Args:
        test_info: Test information
        failed_testcases: List of failed test cases
        failed_patches: List of failed patches
        skipped_patches: List of skipped patches
        pending_patches: List of pending prebuilt patches
        format_type: "html" or "text"
    
    Returns:
        Formatted email content
    """
    formatter = EmailFormatter(test_info)
    
    if failed_testcases:
        for tc in failed_testcases:
            formatter.add_failed_testcase(tc)
    
    if failed_patches:
        for patch in failed_patches:
            formatter.add_failed_patch(patch)
    
    if skipped_patches:
        for patch in skipped_patches:
            formatter.add_skipped_patch(patch)
    
    if pending_patches:
        for patch in pending_patches:
            formatter.add_pending_patch(patch)
    
    if format_type.lower() == "html":
        return formatter.format_html()
    else:
        return formatter.format_plain_text()
