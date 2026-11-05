import os
import stat
import subprocess
from pathlib import Path

ENTRYPOINT = Path(__file__).resolve().parents[1] / "docker-entrypoint.sh"

# Stub logstats: prints its argv one per line.
STUB = '#!/bin/sh\nprintf "%s\\n" "$@"\n'


def run_entrypoint(
    tmp_path: Path, args: list[str], env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "logstats"
    stub.write_text(STUB)
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    full_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", **env}
    return subprocess.run(
        ["/bin/sh", str(ENTRYPOINT), *args],
        env=full_env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_arg_input_is_passed_with_extra_args(tmp_path):
    result = run_entrypoint(tmp_path, ["in.log", "--json"], {})
    assert result.returncode == 0
    assert result.stdout == "in.log\n--json\n"


def test_env_input_used_when_no_args(tmp_path):
    result = run_entrypoint(tmp_path, [], {"LOGSTATS_INPUT": "/data/in.log"})
    assert result.returncode == 0
    assert result.stdout == "/data/in.log\n"


def test_env_output_receives_stdout(tmp_path):
    out = tmp_path / "out.txt"
    env = {"LOGSTATS_INPUT": "/data/in.log", "LOGSTATS_OUTPUT": str(out)}
    result = run_entrypoint(tmp_path, [], env)
    assert result.returncode == 0
    assert result.stdout == ""
    assert out.read_text() == "/data/in.log\n"


def test_arg_overrides_env_input(tmp_path):
    result = run_entrypoint(tmp_path, ["arg.log"], {"LOGSTATS_INPUT": "env.log"})
    assert result.returncode == 0
    assert result.stdout == "arg.log\n"


def test_missing_input_fails(tmp_path):
    result = run_entrypoint(tmp_path, [], {})
    assert result.returncode != 0
    assert "LOGSTATS_INPUT" in result.stderr
