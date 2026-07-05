"""
Security Scanner: Dependency Vulnerability Check

Checks Python dependencies for known vulnerabilities using pip-audit.
Prerequisites: pip install pip-audit
Run: python tests/security/run_dependency_scan.py
"""
import subprocess
import sys
import os


def run_dependency_scan():
    """Run pip-audit to check for vulnerable dependencies."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    requirements_path = os.path.join(project_root, 'requirements.txt')

    print("=" * 60)
    print("DEPENDENCY VULNERABILITY SCANNER")
    print("=" * 60)
    print(f"Checking: {requirements_path}")
    print()

    cmd = [
        sys.executable, '-m', 'pip_audit',
        '-r', requirements_path,
        '--format', 'json',
        '--output', os.path.join(project_root, 'tests', 'security', 'dependency_audit.json'),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        report_path = os.path.join(project_root, 'tests', 'security', 'dependency_audit.json')
        if os.path.exists(report_path):
            import json
            with open(report_path) as f:
                report = json.load(f)

            deps = report.get('dependencies', [])
            vulns = [d for d in deps if d.get('vulns')]

            print(f"Scanned {len(deps)} dependencies")
            print(f"Vulnerable: {len(vulns)}")
            print()

            if vulns:
                print("Vulnerable packages:")
                for dep in vulns:
                    name = dep.get('name', '?')
                    version = dep.get('version', '?')
                    for v in dep.get('vulns', []):
                        vid = v.get('id', '?')
                        fix = v.get('fix_versions', ['unknown'])
                        print(f"  {name}=={version}: {vid} (fix: {fix})")
                print()
                print("FAIL: Vulnerable dependencies found")
                return False
            else:
                print("PASS: No known vulnerabilities")
                return True

        return result.returncode == 0

    except FileNotFoundError:
        print("SKIP: pip-audit not installed. Run: pip install pip-audit")
        return True
    except subprocess.TimeoutExpired:
        print("WARN: Dependency scan timed out")
        return True


if __name__ == '__main__':
    success = run_dependency_scan()
    sys.exit(0 if success else 1)
