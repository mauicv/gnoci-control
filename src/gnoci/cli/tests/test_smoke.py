import pytest
from click.testing import CliRunner
from gnoci.cli import cli

runner = CliRunner()


def invoke(args, expect_exit=0):
    result = runner.invoke(cli, args, catch_exceptions=False)
    assert result.exit_code == expect_exit, (
        f"Command {args!r} exited {result.exit_code}:\n{result.output}"
    )
    return result


# Control commands

def test_start():
    invoke(["start", "--help"])

def test_control_loop():
    invoke(["control-loop", "--limit", "1"])

# Configure commands

def test_test_control_hz():
    invoke(["test-control-hz", "--limit", "1"])

def test_test_hardware():
    invoke(["test-hardware"])

# These commands drive servos through full ranges with sleeps — too slow for smoke tests
def test_run_checks_help():
    invoke(["run-checks", "--help"])

def test_measure_positions_help():
    invoke(["measure-positions", "--help"])

# Storage commands — may fail without GCS credentials in dev

def test_storage_list_experiments():
    result = runner.invoke(cli, ["storage", "list-experiments"], catch_exceptions=True)
    assert result.exit_code in (0, 1), (
        f"Unexpected exit code {result.exit_code}:\n{result.output}"
    )

def test_storage_list_models_help():
    invoke(["storage", "list-models", "--help"])

def test_storage_list_rollouts_help():
    invoke(["storage", "list-rollouts", "--help"])

def test_storage_download_model_help():
    invoke(["storage", "download-model", "--help"])
