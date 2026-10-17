"""Optional per-command Docker isolation. No fallback to host execution.

The operator supplies a digest-pinned image containing the supported toolchains.
Only the disposable scratch directory is mounted; host source/keys are absent.
"""
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

from app.core.config import settings


def command(cmd: list[str], cwd: Path, name: str) -> list[str]:
    image = settings.exec_container_image
    if not re.fullmatch(r"(?:[a-zA-Z0-9./:_-]+@)?sha256:[a-f0-9]{64}", image):
        raise RuntimeError("Container execution requires a digest-pinned EXEC_CONTAINER_IMAGE")
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Docker is unavailable; host execution is disabled in container mode")
    root = str(cwd.resolve())
    def translate(value):
        path = Path(value)
        if path.is_absolute():
            try:
                relative = path.resolve().relative_to(Path(root))
                return "/work" if str(relative)=="." else "/work/"+str(relative)
            except ValueError:
                pass
        return value
    executable = translate(cmd[0])
    if executable == cmd[0] and Path(executable).is_absolute():
        executable = Path(executable).name  # e.g. a host JAVA_HOME tool path
    translated = [executable, *(translate(arg) for arg in cmd[1:])]
    return [docker, "run", "--rm", "--name", name, "--pull=never", "--network=none",
            "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--pids-limit", str(settings.exec_max_processes),
            "--memory", f"{settings.exec_memory_mb}m", "--memory-swap", f"{settings.exec_memory_mb}m",
            "--cpus=1", "--ulimit", "nofile=128:128", "--ulimit", "fsize=16777216:16777216",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--mount", f"type=bind,src={root},dst=/work", "--workdir=/work",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--env", "HOME=/work", "--env", "LANG=C.UTF-8",
            "--entrypoint", "timeout", "-i", image, "--signal=KILL", f"{settings.exec_timeout_seconds}s", *translated]


def cleanup(name: str):
    # The CLI may be killed on timeout before Docker removes its container.
    try:
        subprocess.run([shutil.which("docker") or "docker", "rm", "-f", name],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass  # Docker --rm still applies if the daemon/CLI later reconnects.


def run(cmd: list[str], cwd: Path, stdin: str, host_runner):
    name = "dsa-run-" + uuid.uuid4().hex
    wrapped = command(cmd, cwd, name)
    try:
        result = host_runner(wrapped, cwd, stdin, apply_address_space=False)
        # Docker reserves 125/126/127 for daemon/image/command-start failures.
        # These are infrastructure failures, not failed student test cases.
        if result[0] in (125, 126, 127):
            raise RuntimeError("Container execution infrastructure is unavailable")
        return result
    finally:
        cleanup(name)
