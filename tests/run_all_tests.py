"""
Master Test Runner

Runs all test suites in sequence with coverage reporting.
Provides a summary of results across all testing dimensions.

Usage:
    python tests/run_all_tests.py                  # Run all tests
    python tests/run_all_tests.py --unit           # Unit tests only
    python tests/run_all_tests.py --integration    # Integration tests only
    python tests/run_all_tests.py --security       # Security scans only
    python tests/run_all_tests.py --coverage       # With coverage report
"""
import subprocess
import sys
import os
import time
import argparse


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_suite(name, cmd, description):
    """Run a test suite and return results."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"  {description}")
    print(f"{'=' * 60}")

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        elapsed = time.time() - start
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[-1000:])
        return {
            'name': name,
            'passed': result.returncode == 0,
            'elapsed': elapsed,
            'returncode': result.returncode,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"TIMEOUT after {elapsed:.1f}s")
        return {
            'name': name,
            'passed': False,
            'elapsed': elapsed,
            'returncode': -1,
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {
            'name': name,
            'passed': False,
            'elapsed': 0,
            'returncode': -1,
        }


def main():
    parser = argparse.ArgumentParser(description='Run Scoliosis Brace Coach test suites')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--security', action='store_true', help='Run security scans only')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests only (requires server)')
    parser.add_argument('--load', action='store_true', help='Run load tests only (requires k6)')
    parser.add_argument('--coverage', action='store_true', help='Include coverage report')
    args = parser.parse_args()

    run_all = not (args.unit or args.integration or args.security or args.e2e or args.load)
    results = []

    print("=" * 60)
    print("  SCOLIOSIS BRACE COACH - TEST SUITE RUNNER")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # Unit Tests
    # -----------------------------------------------------------------------
    if run_all or args.unit:
        cmd = [sys.executable, '-m', 'pytest', 'tests/unit/', '-v', '--tb=short', '-x']
        if args.coverage:
            cmd.extend(['--cov=analysis', '--cov=sensors', '--cov-report=term-missing'])
        results.append(run_suite(
            'UNIT TESTS',
            cmd,
            'Fast, isolated tests for all analysis modules and business logic'
        ))

    # -----------------------------------------------------------------------
    # Integration Tests
    # -----------------------------------------------------------------------
    if run_all or args.integration:
        cmd = [sys.executable, '-m', 'pytest', 'tests/integration/', '-v', '--tb=short', '-x']
        if args.coverage:
            cmd.extend(['--cov=app', '--cov-report=term-missing'])
        results.append(run_suite(
            'INTEGRATION TESTS',
            cmd,
            'API endpoint tests, database mutations, request/response contracts'
        ))

    # -----------------------------------------------------------------------
    # Security Tests
    # -----------------------------------------------------------------------
    if run_all or args.security:
        # Pytest security tests
        results.append(run_suite(
            'SECURITY TESTS (Pytest)',
            [sys.executable, '-m', 'pytest', 'tests/security/test_security.py', '-v', '--tb=short'],
            'SQL injection, path traversal, headers, input validation'
        ))

        # Bandit scan
        results.append(run_suite(
            'SECURITY SCAN (Bandit)',
            [sys.executable, 'tests/security/run_bandit.py'],
            'Static analysis for hardcoded secrets, insecure functions'
        ))

        # Dependency audit
        results.append(run_suite(
            'DEPENDENCY AUDIT',
            [sys.executable, 'tests/security/run_dependency_scan.py'],
            'Check dependencies for known vulnerabilities'
        ))

    # -----------------------------------------------------------------------
    # E2E Tests (requires running server)
    # -----------------------------------------------------------------------
    if args.e2e:
        results.append(run_suite(
            'E2E TESTS (Playwright)',
            [sys.executable, '-m', 'pytest', 'tests/e2e/', '-v', '--tb=short', '-m', 'not slow'],
            'Browser-based user journey tests (requires server at :5000)'
        ))

    # -----------------------------------------------------------------------
    # Load Tests (requires k6)
    # -----------------------------------------------------------------------
    if args.load:
        results.append(run_suite(
            'LOAD TESTS (k6)',
            ['k6', 'run', 'tests/load/k6_api_load.js'],
            'Performance and concurrency testing'
        ))

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  TEST RESULTS SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    total_time = sum(r['elapsed'] for r in results)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['name']} ({r['elapsed']:.1f}s)")

    print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"  Total time: {total_time:.1f}s")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
