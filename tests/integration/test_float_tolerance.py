import pytest

@pytest.fixture
def testcases_initial():
    return {
        "passed": (
            """
            def test_passed(snapshot):
                assert snapshot == 3.0
            """
        ),
        "failed": (
            """
            def test_failed(snapshot):
                # comment to keep structure
                assert snapshot == 4.0
            """
        ),
    }


@pytest.fixture
def generate_snapshots(testdir, testcases_initial):
    testdir.makepyfile(test_file=testcases_initial["passed"])
    result = testdir.runpytest("-v", "--snapshot-update")
    return result, testdir, testcases_initial


@pytest.mark.xfail(strict=False)
def test_generated_snapshots(generate_snapshots):
    result = generate_snapshots[0]
    result.stdout.re_match_lines((r"1 snapshot generated\.",))
    assert "snapshots unused" not in result.stdout.str()
    assert result.ret == 0


@pytest.mark.xfail(strict=False)
def test_approximate_match(generate_snapshots, plugin_args_fails_xdist):
    testdir = generate_snapshots[1]
    testdir.makepyfile(
        test_file="""
            def test_passed(snapshot):
                assert snapshot == 3.2
            """
    )
    result = testdir.runpytest("-v", "--snapshot-abs-tol=0.5", *plugin_args_fails_xdist)
    result.stdout.re_match_lines((r"test_file.py::test_passed PASSED",))
    assert result.ret == 0


@pytest.mark.xfail(strict=False)
def test_failed_snapshots(generate_snapshots):
    testdir = generate_snapshots[1]
    testdir.makepyfile(test_file=generate_snapshots[2]["failed"])
    result = testdir.runpytest("-v", "--snapshot-abs-tol=0.1")
    result.stdout.re_match_lines((r"1 snapshot failed\.",))
    assert result.ret == 1
