"""Smoke test that proves the build/test harness works (TASK-001)."""

import trendidea


def test_package_imports():
    assert trendidea.__version__ == "0.1.0"
