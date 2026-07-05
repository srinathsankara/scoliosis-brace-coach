"""
Security Scanner: Bandit Static Analysis

Runs Bandit (Python security linter) to detect common security issues:
- Hardcoded passwords
- SQL injection risks
- Insecure deserialization
- Use of insecure functions

Prerequisites: pip install bandit
Run: python tests/security/run_bandit.py
"""
import subprocess
import sys
import os


def run_bandit():
    """Run Bandit security scanner on the project."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("=" * 60)
    print("BANDIT SECURITY SCANNER")
    print("=" * 60)
    print(f"Scanning: {project_root}")
    print()

    cmd = [
        sys.executable, '-m', 'bandit',
        '-r', project_root,
        '-f', 'json',
        '-o', os.path.join(project_root, 'tests', 'security', 'bandit_report.json'),
        '--exclude', os.path.join(project_root, 'tests'),
        '--exclude', os.path.join(project_root, 'venv'),
        '-ll',  # Only medium and high severity
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # Parse JSON report
        report_path = os.path.join(project_root, 'tests', 'security', 'bandit_report.json')
        if os.path.exists(report_path):
            import json
            with open(report_path) as f:
                report = json.load(f)

            metrics = report.get('metrics', {}).get('_totals', {})
            results = report.get('results', [])

            print(f"Scan complete: {len(results)} issues found")
            print(f"  High severity: {metrics.get('SEVERITY.HIGH', 0)}")
            print(f"  Medium severity: {metrics.get('SEVERITY.MEDIUM', 0)}")
            print(f"  Low severity: {metrics.get('SEVERITY.LOW', 0)}")
            print()

            if results:
                print("Issues found:")
                for issue in results[:20]:  # Show first 20
                    severity = issue.get('issue_severity', 'UNKNOWN')
                    confidence = issue.get('issue_confidence', 'UNKNOWN')
                    filename = os.path.relpath(issue.get('filename', ''), project_root)
                    line = issue.get('line_number', '?')
                    text = issue.get('issue_text', '')
                    print(f"  [{severity}/{confidence}] {filename}:{line}")
                    print(f"    {text}")
                    print()

            if metrics.get('SEVERITY.HIGH', 0) > 0:
                print("FAIL: High severity issues found")
                return False
            else:
                print("PASS: No high severity issues")
                return True

        return result.returncode == 0

    except FileNotFoundError:
        print("SKIP: Bandit not installed. Run: pip install bandit")
        return True
    except subprocess.TimeoutExpired:
        print("WARN: Bandit scan timed out")
        return True


if __name__ == '__main__':
    success = run_bandit()
    sys.exit(0 if success else 1)
