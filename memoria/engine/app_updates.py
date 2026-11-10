"""Opt-in Git updates and a stdlib-only, snapshotted post-exit helper.

The UI owns consent and orderly shutdown. ``ready`` means the helper holds a
handle to the original process, not that it has permission to update a running
app. The replacement app writes ``MEMORIA_UPDATE_READY`` after showing its main
window. No Qt or third-party imports belong in this module.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import stat
import subprocess
import sys
import threading
import time
import tomllib
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Callable


GIT_TIMEOUT = 90
INSTALL_TIMEOUT = 900
EXIT_TIMEOUT = 120
STARTUP_TIMEOUT = 90
MANIFESTS = ("requirements.txt", "pyproject.toml")


class UpdateError(RuntimeError):
    """An update could not be checked or safely completed."""


class _Cancelled(UpdateError):
    pass


@dataclass
class UpdateInfo:
    repo: Path
    branch: str
    remote: str
    upstream: str
    local_head: str
    remote_head: str
    ahead: int
    behind: int
    dirty: list[str]
    changed_manifests: tuple[str, ...]
    remote_fingerprint: str = field(default="", repr=False)

    @property
    def can_update(self) -> bool:
        return self.behind > 0 and self.ahead == 0 and not self.dirty

    @property
    def summary(self) -> str:
        if self.ahead and self.behind:
            message = (
                f"Branches have diverged ({self.ahead} local, {self.behind} upstream "
                "commits). Resolve this manually; automatic update is blocked."
            )
        elif self.ahead:
            message = (
                f"Checkout has {self.ahead} local commit(s) ahead of upstream. "
                "Automatic update is blocked."
            )
        elif self.behind:
            message = f"An update is available ({self.behind} new commit(s))."
        else:
            message = "Up to date with the configured upstream."
        if self.dirty:
            message += (
                f" Checkout has {len(self.dirty)} tracked/untracked change(s); "
                "commit or move them before updating. Nothing will be stashed or deleted."
            )
        return message


@dataclass
class Handoff:
    """``ready`` exists only after the helper holds the exact original process handle."""

    directory: Path
    ready: Path
    cancel: Path
    result: Path
    log: Path
    pid: int


@dataclass(frozen=True)
class _Checkout:
    branch: str
    head: str
    remote: str
    upstream: str
    fingerprint: str


@dataclass(frozen=True)
class _Environment:
    python: Path
    pythonw: Path
    version: tuple[int, ...]


def _redact(text: str) -> str:
    text = re.sub(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>\"']+", "[remote URL]", text)
    text = re.sub(r"\b[^\s/@:]+@[^\s/:]+:[^\s]+", "[remote address]", text)
    return text


def _git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        GIT_TERMINAL_PROMPT="0",
        GCM_INTERACTIVE="Never",
        GIT_ASKPASS="",
        SSH_ASKPASS="",
        SSH_ASKPASS_REQUIRE="never",
        GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=20",
        GIT_PAGER="cat",
        GIT_OPTIONAL_LOCKS="0",
    )
    # A caller's Git process context must not redirect this operation elsewhere.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    return env


def _git(repo: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> str:
    command = [
        "git", "-c", f"core.hooksPath={os.devnull}",
        "-c", "core.askPass=", "-c", "credential.interactive=false",
        "-c", "protocol.ext.allow=never", "-C", str(repo), *args,
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=GIT_TIMEOUT, env=_git_environment(), stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except FileNotFoundError as exc:
        raise UpdateError("Git was not found. Install Git for Windows and restart Memoria.") from exc
    except subprocess.TimeoutExpired as exc:
        raise UpdateError("Git timed out. Check network access and try checking again.") from exc
    except OSError as exc:
        raise UpdateError(f"Unable to run Git: {_redact(str(exc))}") from exc
    if result.returncode not in allowed:
        detail = _redact((result.stderr or result.stdout).strip())[-6000:]
        raise UpdateError(f"Git {args[0]} failed: {detail or 'unknown error'}")
    return result.stdout


def _validate_repo(repo: Path) -> Path:
    if getattr(sys, "frozen", False):
        raise UpdateError(
            "Packaged builds cannot update using Git. Install a new packaged release instead."
        )
    root = Path(repo).resolve()
    if not root.is_dir() or not (root / ".git").exists() or not (root / "Memoria.pyw").is_file():
        raise UpdateError(
            "Git self-update requires a Memoria source checkout with .git and Memoria.pyw. "
            "Installed packages and packaged builds must be updated separately."
        )
    top = Path(_git(root, "rev-parse", "--show-toplevel").strip()).resolve()
    if top != root:
        raise UpdateError("Self-update must run from the canonical Memoria repository root.")
    if _git(root, "rev-parse", "--is-bare-repository").strip() != "false":
        raise UpdateError("A bare Git repository cannot run or update Memoria.")
    return root


def source_root() -> Path:
    """Return the canonical source checkout, or explain why Git update is unavailable."""
    return _validate_repo(Path(__file__).resolve().parents[2])


def _checkout(repo: Path) -> _Checkout:
    branch = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1)).strip()
    if not branch:
        raise UpdateError("HEAD is detached. Switch to a branch with a configured upstream first.")
    remote = _git(repo, "config", "--get", f"branch.{branch}.remote", allowed=(0, 1)).strip()
    upstream = _git(repo, "config", "--get", f"branch.{branch}.merge", allowed=(0, 1)).strip()
    if not remote or not upstream:
        raise UpdateError("This branch has no configured upstream. Configure tracking in Git first.")
    if not upstream.startswith("refs/heads/") or any(c in upstream for c in "\r\n"):
        raise UpdateError("The configured upstream must be a single branch reference.")
    if remote != ".":
        names = _git(repo, "remote").splitlines()
        if remote not in names or any(c in remote for c in "\r\n:@"):
            raise UpdateError("The configured upstream remote is not a valid named Git remote.")
        address = _git(repo, "remote", "get-url", "--all", remote)
    else:
        address = str(repo)
    fingerprint = hashlib.sha256(address.encode("utf-8")).hexdigest()
    head = _git(repo, "rev-parse", "--verify", "HEAD").strip()
    return _Checkout(branch, head, remote, upstream, fingerprint)


def _dirty(repo: Path) -> list[str]:
    entries = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
    changes = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        if entry:
            changes.append(entry)
            if "R" in entry[:2] or "C" in entry[:2]:
                index += 1
        index += 1
    return changes


@contextmanager
def _fetched(repo: Path, remote: str, upstream: str):
    reference = f"refs/memoria-updates/{uuid.uuid4().hex}"
    try:
        _git(
            repo, "fetch", "--no-tags", "--no-write-fetch-head", "--no-recurse-submodules",
            "--no-auto-maintenance", "--refmap=", "--", remote, f"+{upstream}:{reference}",
        )
        yield _git(repo, "rev-parse", "--verify", f"{reference}^{{commit}}").strip()
    finally:
        _git(repo, "update-ref", "-d", reference)


def _changed_manifests(repo: Path, old: str, new: str) -> tuple[str, ...]:
    names = _git(repo, "diff", "--name-only", "-z", old, new, "--", *MANIFESTS).split("\0")
    return tuple(name for name in MANIFESTS if name in names)


def check(repo: Path | None = None) -> UpdateInfo:
    """Fetch only a private temporary ref; never pull or change the working tree."""
    root = source_root() if repo is None else _validate_repo(repo)
    initial = _checkout(root)
    with _fetched(root, initial.remote, initial.upstream) as target:
        ahead, behind = map(
            int, _git(root, "rev-list", "--left-right", "--count", f"{initial.head}...{target}").split()
        )
        manifests = _changed_manifests(root, initial.head, target)
        if _checkout(root) != initial:
            raise UpdateError("Checkout or upstream changed during the check. Check again.")
        return UpdateInfo(
            root, initial.branch, initial.remote, initial.upstream, initial.head,
            target, ahead, behind, _dirty(root), manifests, initial.fingerprint,
        )


def _python_environment() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("PYTHONHOME", "PYTHONPATH", "PIP_TARGET", "PIP_PREFIX", "PIP_ROOT", "PIP_USER"):
        env.pop(key, None)
    env.update(
        PIP_CONFIG_FILE=os.devnull, PIP_NO_INPUT="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
        PIP_REQUIRE_VIRTUALENV="true", PYTHONNOUSERSITE="1",
    )
    return env


def _managed_environment(repo: Path) -> _Environment:
    venv = repo / ".venv"
    python = venv / "Scripts" / "python.exe"
    pythonw = venv / "Scripts" / "pythonw.exe"
    if (
        not (venv / "pyvenv.cfg").is_file()
        or not python.is_file() or not pythonw.is_file()
        or not venv.resolve().is_relative_to(repo)
        or not python.resolve().is_relative_to(venv.resolve())
        or not pythonw.resolve().is_relative_to(venv.resolve())
    ):
        raise UpdateError(
            "Automatic update requires this checkout's managed .venv with python.exe and "
            "pythonw.exe. Run run.ps1 to create it; system Python will never be modified."
        )
    try:
        result = subprocess.run(
            [str(python), "-I", "-c",
             "import json,sys; print(json.dumps([sys.prefix,sys.base_prefix,list(sys.version_info[:3])]))"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
            stdin=subprocess.DEVNULL, env=_python_environment(),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), check=True,
        )
        prefix, base, version = json.loads(result.stdout)
        if Path(prefix).resolve() != venv.resolve() or Path(prefix).resolve() == Path(base).resolve():
            raise ValueError("the interpreter is not running inside the managed environment")
        if tuple(version) < (3, 11):
            raise ValueError("Python 3.11 or newer is required")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise UpdateError(f"The managed .venv is not usable: {_redact(str(exc))}") from exc
    return _Environment(python, pythonw, tuple(version))


def _updates_root() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    return base / "Memoria" / "updates"


def mark_restart_ready() -> None:
    """Acknowledge the first shown window of an updater-launched app, once only."""
    value = os.environ.pop("MEMORIA_UPDATE_READY", None)
    if not value:
        return
    path = Path(value)
    root = _updates_root().resolve()
    if (
        not path.is_absolute()
        or path.parent.resolve().parent != root
        or not re.fullmatch(r"[0-9a-f]{32}", path.parent.name)
        or not re.fullmatch(r"startup-[0-9a-f]{32}\.ready", path.name)
        or not path.parent.is_dir()
    ):
        raise UpdateError("The update startup marker is not in Memoria's update directory.")
    try:
        with path.open("x", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "ready": True}, stream)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise UpdateError(f"Unable to confirm updated Memoria startup: {_redact(str(exc))}") from exc


def _write_json(path: Path, value: dict) -> None:
    staging = path.with_name(path.name + ".writing")
    with staging.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(staging, path)


class _WindowsProcess:
    """Hold an exact process handle, checking creation time to prevent PID reuse."""

    def __init__(self, pid: int, expected_creation: int | None = None):
        if os.name != "nt":
            raise UpdateError("Automatic restart updates are supported only on Windows.")
        from ctypes import wintypes

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.api.WaitForSingleObject.restype = wintypes.DWORD
        self.api.GetProcessTimes.argtypes = [wintypes.HANDLE] + [
            ctypes.POINTER(wintypes.FILETIME)
        ] * 4
        self.api.GetProcessTimes.restype = wintypes.BOOL
        self.handle = self.api.OpenProcess(0x00100000 | 0x1000, False, pid)
        if not self.handle:
            raise UpdateError("Unable to watch the original application process. Update cancelled.")
        created, exited, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not self.api.GetProcessTimes(
            self.handle, ctypes.byref(created), ctypes.byref(exited),
            ctypes.byref(kernel), ctypes.byref(user),
        ):
            self.close()
            raise UpdateError("Unable to verify the original application process.")
        self.creation = (created.dwHighDateTime << 32) | created.dwLowDateTime
        if expected_creation is not None and self.creation != expected_creation:
            self.close()
            raise UpdateError("The original application process changed. Check for updates again.")

    def exited(self) -> bool:
        result = self.api.WaitForSingleObject(self.handle, 0)
        if result == 0:
            return True
        if result == 258:
            return False
        raise UpdateError("Unable to wait for the original application to close.")

    def close(self) -> None:
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def _expected(info: UpdateInfo, *, updated: bool = False) -> _Checkout:
    return _Checkout(
        info.branch, info.remote_head if updated else info.local_head,
        info.remote, info.upstream, info.remote_fingerprint,
    )


def _validate_approved(info: UpdateInfo, *, updated: bool = False) -> None:
    if not info.remote_fingerprint or _checkout(info.repo) != _expected(info, updated=updated):
        raise UpdateError("Branch, HEAD, remote, or upstream changed. Check for updates again.")
    if _dirty(info.repo):
        raise UpdateError(
            "The checkout has tracked or untracked changes. Commit or move them, then check "
            "again. Nothing was stashed, reset, or deleted."
        )


def launch_update(info: UpdateInfo) -> Handoff:
    """Snapshot the helper and approved target, then launch a waiting console."""
    if os.name != "nt":
        raise UpdateError("Automatic restart updates are supported only on Windows.")
    root = _validate_repo(info.repo)
    if root != info.repo or not info.can_update:
        raise UpdateError("This checkout is not eligible for a clean fast-forward update. Check again.")
    _validate_approved(info)
    environment = _managed_environment(root)
    parent = _WindowsProcess(os.getpid())
    try:
        creation = parent.creation
    finally:
        parent.close()
    directory = (_updates_root() / uuid.uuid4().hex).resolve()
    if directory.is_relative_to(root):
        raise UpdateError("Update helper storage must be outside the source checkout.")
    handoff = Handoff(
        directory, directory / "ready.json", directory / "cancel",
        directory / "result.json", directory / "update.log", 0,
    )
    try:
        directory.mkdir(parents=True, mode=0o700)
        helper = directory / "helper.py"
        with helper.open("xb") as stream:
            stream.write(Path(__file__).read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        approved = asdict(info)
        approved["repo"] = str(root)
        request = directory / "request.json"
        _write_json(request, {
            "version": 1, "approved": approved, "parent_pid": os.getpid(),
            "parent_creation": creation,
        })
        helper.chmod(stat.S_IREAD)
        request.chmod(stat.S_IREAD)
        process = subprocess.Popen(
            [str(environment.python), "-I", str(helper), str(request)],
            cwd=str(directory), env=_python_environment(), close_fds=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        handoff.pid = process.pid
    except OSError as exc:
        message = f"Unable to launch the update helper: {_redact(str(exc))}"
        if directory.is_dir():
            _write_json(handoff.result, {"phase": "failed", "status": "failed", "message": message})
            handoff.log.write_text(message + "\n", encoding="utf-8")
        raise UpdateError(message) from exc
    return handoff


class _Progress:
    def __init__(self, directory: Path):
        self.directory = directory
        self.phase = "starting"

    def log(self, message: str) -> None:
        message = _redact(message).rstrip()
        print(message, flush=True)
        with (self.directory / "update.log").open("a", encoding="utf-8") as stream:
            stream.write(message + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def set(self, phase: str, message: str, **extra) -> None:
        self.phase = phase
        self.log(message)
        _write_json(self.directory / "result.json", {
            "phase": phase,
            "status": phase if phase in ("success", "failed", "cancelled") else "running",
            "message": _redact(message), "time": time.time(),
            **({"error": _redact(message)} if phase == "failed" else {}), **extra,
        })


def _wait_for_parent(request: dict, directory: Path, progress: _Progress) -> None:
    parent = _WindowsProcess(request["parent_pid"], request["parent_creation"])
    try:
        progress.set("waiting_for_exit", "Waiting for Memoria to finish its work and close...")
        _write_json(directory / "ready.json", {"pid": os.getpid(), "parent_pid": request["parent_pid"]})
        deadline = time.monotonic() + EXIT_TIMEOUT
        while True:
            if (directory / "cancel").exists():
                raise _Cancelled("Update cancelled. The checkout has not been changed.")
            if parent.exited():
                return
            if time.monotonic() >= deadline:
                raise UpdateError(
                    "Memoria did not close within 120 seconds. No update was applied. "
                    "Finish pending tasks and try again."
                )
            time.sleep(0.1)
    finally:
        parent.close()


@contextmanager
def _update_lock(repo: Path):
    common = Path(_git(repo, "rev-parse", "--git-common-dir").strip())
    common = (repo / common).resolve() if not common.is_absolute() else common.resolve()
    path = common / "memoria-update.lock"
    token = uuid.uuid4().hex
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise UpdateError(
            "Another updater holds memoria-update.lock in the Git directory. Wait for it. "
            "If a previous updater crashed, close it and inspect its log before removing "
            "that stale lock manually."
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "token": token}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        if path.exists() and json.loads(path.read_text(encoding="utf-8")).get("token") == token:
            path.unlink()


def _supports_python(requirement: str, version: tuple[int, ...]) -> bool:
    if not isinstance(requirement, str) or not requirement.strip():
        raise UpdateError("pyproject.toml has an invalid project.requires-python value.")
    current = tuple(version[:3])
    supported = True
    for part in requirement.split(","):
        match = re.fullmatch(r"\s*(>=|<=|==|!=|~=|>|<)\s*(\d+(?:\.\d+){0,2})(\.\*)?\s*", part)
        if not match:
            raise UpdateError(
                "Cannot safely evaluate the new Python requirement. Update Python and "
                "dependencies manually; automatic update was not applied."
            )
        operator, number, wildcard = match.groups()
        pieces = tuple(map(int, number.split(".")))
        target = pieces + (0,) * (3 - len(pieces))
        if wildcard:
            if operator not in ("==", "!="):
                raise UpdateError("Invalid wildcard in project.requires-python.")
            equal = current[:len(pieces)] == pieces
            matches = equal if operator == "==" else not equal
        elif operator == "~=":
            if len(pieces) < 2:
                raise UpdateError("Invalid compatible version in project.requires-python.")
            upper = (pieces[0] + 1, 0, 0) if len(pieces) == 2 else (pieces[0], pieces[1] + 1, 0)
            matches = target <= current < upper
        else:
            matches = {
                ">=": current >= target, "<=": current <= target, ">": current > target,
                "<": current < target, "==": current == target, "!=": current != target,
            }[operator]
        supported = supported and matches
    return supported


def _dependency_arguments(info: UpdateInfo, environment: _Environment) -> list[str]:
    launcher = _git(info.repo, "ls-tree", info.remote_head, "--", "Memoria.pyw").splitlines()
    if len(launcher) != 1 or launcher[0].split()[:2] not in (["100644", "blob"], ["100755", "blob"]):
        raise UpdateError("The update removes or replaces the application launcher. "
                          "Follow the upstream migration instructions and update manually.")
    entries = _git(info.repo, "ls-tree", info.remote_head, "--", *MANIFESTS).splitlines()
    available = {}
    for entry in entries:
        metadata, name = entry.split("\t", 1)
        mode, kind, _ = metadata.split()
        if mode not in ("100644", "100755") or kind != "blob":
            raise UpdateError(f"{name} must be a regular file, not a symlink or submodule.")
        available[name] = _git(info.repo, "show", f"{info.remote_head}:{name}")
    removed = set(info.changed_manifests) - available.keys()
    if removed:
        raise UpdateError(
            f"Dependency manifest removed ({', '.join(sorted(removed))}). "
            "Follow the upstream migration instructions and update manually."
        )
    project = {}
    if "pyproject.toml" in available:
        try:
            document = tomllib.loads(available["pyproject.toml"])
            project = document.get("project", {})
            if not isinstance(project, dict):
                raise ValueError("project must be a table")
        except (ValueError, tomllib.TOMLDecodeError) as exc:
            raise UpdateError(f"Invalid pyproject.toml: {_redact(str(exc))}") from exc
        if "requires-python" in project and not _supports_python(
            project["requires-python"], environment.version
        ):
            version = ".".join(map(str, environment.version))
            raise UpdateError(
                f"The update requires Python {project['requires-python']}; the managed "
                f"environment uses {version}. Upgrade Python and recreate .venv manually first."
            )
    if not info.changed_manifests:
        return []
    if "dependencies" in project.get("dynamic", []):
        raise UpdateError("Dynamic project dependencies require a manual update.")
    dependencies = project.get("dependencies", [])
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) and item.strip() and not item.lstrip().startswith("-")
        and "\n" not in item and "\r" not in item for item in dependencies
    ):
        raise UpdateError("Invalid project.dependencies in pyproject.toml; update was not applied.")
    arguments = []
    if "requirements.txt" in available:
        arguments.extend(["-r", str(info.repo / "requirements.txt")])
    arguments.extend(dependencies)
    return arguments


def _stream_command(command: list[str], repo: Path, progress: _Progress) -> None:
    progress.log("Managed dependency command: " + subprocess.list2cmdline(command))
    try:
        process = subprocess.Popen(
            command, cwd=str(repo), env=_python_environment(),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", close_fds=True,
        )
    except OSError as exc:
        raise UpdateError(f"Unable to start dependency installation: {_redact(str(exc))}") from exc
    lines: queue.Queue[str | None] = queue.Queue()

    def read_output():
        try:
            assert process.stdout is not None
            for line in process.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    deadline = time.monotonic() + INSTALL_TIMEOUT
    finished_output = False
    try:
        while not finished_output or process.poll() is None:
            if time.monotonic() >= deadline:
                raise UpdateError(
                    "Dependency installation timed out. The source may already be updated; "
                    "review this log and repair .venv before restarting."
                )
            try:
                line = lines.get(timeout=0.1)
                if line is None:
                    finished_output = True
                else:
                    progress.log(line)
            except queue.Empty:
                pass
        if process.wait(timeout=5) != 0:
            raise UpdateError(
                "Dependency installation failed. The source has been updated, but Memoria "
                "was not restarted. Review the pip errors above, repair the managed .venv "
                "using the dependency command in this log, then start with run.ps1. "
                "No rollback was attempted."
            )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        reader.join(timeout=2)
        if not reader.is_alive() and process.stdout is not None:
            process.stdout.close()


def _apply_update(
    info: UpdateInfo, progress: _Progress, cancelled: Callable[[], bool] = lambda: False,
) -> _Environment:
    root = _validate_repo(info.repo)
    if root != info.repo or not info.can_update:
        raise UpdateError("The approved request is not a clean fast-forward update.")
    with _update_lock(root):
        progress.set("validating", "Rechecking checkout, branch, upstream and managed Python...")
        _validate_approved(info)
        environment = _managed_environment(root)
        if cancelled():
            raise _Cancelled("Update cancelled. The checkout has not been changed.")
        progress.set("fetching", "Confirming the exact approved upstream commit...")
        with _fetched(root, info.remote, info.upstream) as target:
            if target != info.remote_head:
                raise UpdateError("Upstream changed after approval. No update applied; check again.")
            _validate_approved(info)
            counts = _git(root, "rev-list", "--left-right", "--count", f"{info.local_head}...{target}")
            ahead, behind = map(int, counts.split())
            if ahead or not behind:
                raise UpdateError("The approved target is no longer a fast-forward. Check again.")
            if _changed_manifests(root, info.local_head, target) != info.changed_manifests:
                raise UpdateError("The approved dependency manifest list changed. Check again.")
            arguments = _dependency_arguments(info, environment)
            if cancelled():
                raise _Cancelled("Update cancelled. The checkout has not been changed.")
            _validate_approved(info)
            progress.set("updating", f"Fast-forwarding to approved commit {target[:12]}...")
            _git(root, "merge", "--ff-only", "--no-edit", "--no-overwrite-ignore", target)
            _validate_approved(info, updated=True)
        if arguments:
            progress.set("installing_dependencies", "Installing changed dependencies into .venv...")
            _stream_command(
                [str(environment.python), "-I", "-m", "pip", "--disable-pip-version-check",
                 "install", "--no-input", "--no-user", "--prefix", str(root / ".venv"), *arguments],
                root, progress,
            )
        else:
            progress.log("No changed dependencies need installation.")
        _validate_approved(info, updated=True)
        return environment


def _restart(info: UpdateInfo, environment: _Environment, progress: _Progress) -> None:
    sentinel = progress.directory / f"startup-{uuid.uuid4().hex}.ready"
    env = _python_environment()
    env["MEMORIA_UPDATE_READY"] = str(sentinel)
    progress.set("restarting", "Starting updated Memoria...")
    try:
        process = subprocess.Popen(
            [str(environment.pythonw), str(info.repo / "Memoria.pyw")],
            cwd=str(info.repo), env=env, close_fds=True,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    except OSError as exc:
        raise UpdateError(f"Unable to restart Memoria: {_redact(str(exc))}") from exc
    progress.set("waiting_for_startup", "Waiting for Memoria's main window...", pid=process.pid)
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while True:
        code = process.poll()
        if code is not None:
            raise UpdateError(
                f"Updated Memoria exited before becoming ready (exit code {code}). "
                "Review this log and start it manually after fixing the startup error."
            )
        if sentinel.is_file():
            progress.set("success", "Update complete. Memoria is ready.", pid=process.pid)
            return
        if time.monotonic() >= deadline:
            raise UpdateError(
                "Memoria was launched but did not confirm startup within 90 seconds. "
                "Check its window before starting another copy. The process was not killed."
            )
        time.sleep(0.2)


def _load_request(path: Path) -> dict:
    request = json.loads(path.read_text(encoding="utf-8"))
    if request.get("version") != 1:
        raise UpdateError("Unsupported update request. Check for updates again.")
    raw = request["approved"]
    raw["repo"] = Path(raw["repo"])
    raw["changed_manifests"] = tuple(raw["changed_manifests"])
    info = UpdateInfo(**raw)
    if not info.repo.is_absolute() or not info.can_update:
        raise UpdateError("Invalid approved update request.")
    if any(not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head) for head in (
        info.local_head, info.remote_head,
    )):
        raise UpdateError("Invalid approved commit identifier.")
    request["info"] = info
    return request


def _run_helper(request_path: Path) -> str:
    directory = request_path.resolve().parent
    progress = _Progress(directory)
    try:
        request = _load_request(request_path)
        if directory.is_relative_to(request["info"].repo.resolve()):
            raise UpdateError("The standalone helper must run outside the checkout.")
        _wait_for_parent(request, directory, progress)
        if (directory / "cancel").exists():
            raise _Cancelled("Update cancelled. The checkout has not been changed.")
        environment = _apply_update(
            request["info"], progress, lambda: (directory / "cancel").exists(),
        )
        _restart(request["info"], environment, progress)
        return "success"
    except _Cancelled as exc:
        progress.set("cancelled", str(exc))
        return "cancelled"
    except Exception as exc:
        failed_phase = progress.phase
        progress.set(
            "failed", f"Update failed: {_redact(str(exc))}", failed_phase=failed_phase,
            log=str(directory / "update.log"),
        )
        progress.log("No reset, stash, deletion of local changes, or automatic rollback was performed.")
        return "failed"


def _main() -> int:
    if len(sys.argv) != 2:
        print("This standalone helper must be launched by Memoria's update controller.")
        return 2
    status = _run_helper(Path(sys.argv[1]))
    if status == "failed":
        try:
            input("\nUpdate failed. The log above is retained. Press Enter to close this window...")
        except (EOFError, OSError):
            pass
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
