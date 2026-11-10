import json
import os
from pathlib import Path
import stat
import subprocess
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from memoria.engine import app_updates as updates


def git(repo, *args):
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never")
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    return subprocess.run(
        ["git", "-C", str(repo), *args], env=env, check=True, capture_output=True,
        text=True, encoding="utf-8", timeout=20,
    ).stdout.strip()


def commit(repo, name, content, message="change"):
    (repo / name).write_text(content, encoding="utf-8")
    git(repo, "add", "--", name)
    git(repo, "commit", "--quiet", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repositories(tmp_path):
    upstream = tmp_path / "upstream with spaces"
    local = tmp_path / "checkout with spaces"
    upstream.mkdir()
    git(upstream, "init", "--quiet", "--initial-branch=release-line")
    git(upstream, "config", "user.name", "Updater Tests")
    git(upstream, "config", "user.email", "updater@example.invalid")
    (upstream / "Memoria.pyw").write_text("print('fixture')\n", encoding="utf-8")
    (upstream / ".gitignore").write_text(".venv/\nignored.txt\n", encoding="utf-8")
    (upstream / "requirements.txt").write_text("example-package>=1\n", encoding="utf-8")
    (upstream / "pyproject.toml").write_text(
        '[project]\nname="test"\nrequires-python=">=3.11"\ndependencies=["example-package>=1"]\n',
        encoding="utf-8",
    )
    git(upstream, "add", ".")
    git(upstream, "commit", "--quiet", "-m", "initial")
    git(tmp_path, "clone", "--quiet", "--origin", "team", str(upstream), str(local))
    git(local, "config", "user.name", "Updater Tests")
    git(local, "config", "user.email", "updater@example.invalid")
    return upstream, local


@pytest.fixture
def approved(repositories):
    upstream, local = repositories
    commit(upstream, "feature.txt", "a new feature\n")
    return upstream, local, updates.check(local)


@pytest.fixture
def managed(monkeypatch, repositories):
    _, local = repositories
    environment = updates._Environment(
        local / ".venv" / "Scripts" / "python.exe",
        local / ".venv" / "Scripts" / "pythonw.exe",
        (3, 12, 10),
    )
    monkeypatch.setattr(updates, "_managed_environment", lambda root: environment)
    return environment


@pytest.fixture
def progress(tmp_path):
    directory = tmp_path / "handoff"
    directory.mkdir()
    return updates._Progress(directory)


def request_file(info, progress):
    raw = asdict(info)
    raw["repo"] = str(info.repo)
    path = progress.directory / "request.json"
    path.write_text(json.dumps({
        "version": 1, "approved": raw, "parent_pid": 123, "parent_creation": 456,
    }), encoding="utf-8")
    return path


def test_check_fetches_private_ref_without_touching_checkout(repositories):
    upstream, local = repositories
    old = git(local, "rev-parse", "HEAD")
    tracking = git(local, "rev-parse", "refs/remotes/team/release-line")
    old_index = (local / ".git" / "index").read_bytes()
    target = commit(upstream, "feature.txt", "upstream only\n")
    info = updates.check(local)
    assert info.repo == local.resolve()
    assert info.branch == "release-line"
    assert info.remote == "team"
    assert info.upstream == "refs/heads/release-line"
    assert (info.local_head, info.remote_head) == (old, target)
    assert (info.ahead, info.behind) == (0, 1)
    assert info.can_update
    assert "available" in info.summary
    assert git(local, "rev-parse", "HEAD") == old
    assert git(local, "rev-parse", "refs/remotes/team/release-line") == tracking
    assert not (local / "feature.txt").exists()
    assert not (local / ".git" / "FETCH_HEAD").exists()
    assert git(local, "for-each-ref", "refs/memoria-updates/") == ""
    assert (local / ".git" / "index").read_bytes() == old_index


def test_up_to_date(repositories):
    _, local = repositories
    info = updates.check(local)
    assert not info.can_update
    assert (info.ahead, info.behind) == (0, 0)
    assert "Up to date" in info.summary


@pytest.mark.parametrize("kind", ["tracked", "untracked", "diagnostics"])
def test_dirty_files_block_update(approved, kind):
    _, local, _ = approved
    name = {
        "tracked": "Memoria.pyw", "untracked": "new.txt", "diagnostics": "diagnostics.json",
    }[kind]
    (local / name).write_text("local data", encoding="utf-8")
    info = updates.check(local)
    assert not info.can_update
    assert len(info.dirty) == 1
    assert name in info.dirty[0]
    assert "tracked/untracked" in info.summary
    assert (local / name).read_text(encoding="utf-8") == "local data"


@pytest.mark.parametrize("diverged", [False, True])
def test_ahead_and_diverged(repositories, diverged):
    upstream, local = repositories
    commit(local, "local.txt", "local commit")
    if diverged:
        commit(upstream, "remote.txt", "upstream commit")
    info = updates.check(local)
    assert not info.can_update
    assert info.ahead == 1
    assert info.behind == int(diverged)
    assert ("diverged" if diverged else "ahead") in info.summary


def test_detached_and_missing_upstream_are_errors(repositories):
    _, local = repositories
    git(local, "checkout", "--detach", "--quiet")
    with pytest.raises(updates.UpdateError, match="detached"):
        updates.check(local)
    git(local, "checkout", "--quiet", "release-line")
    git(local, "branch", "--unset-upstream")
    with pytest.raises(updates.UpdateError, match="no configured upstream"):
        updates.check(local)


def test_frozen_and_non_checkout_are_explained(tmp_path, monkeypatch):
    with pytest.raises(updates.UpdateError, match="source checkout"):
        updates.check(tmp_path)
    monkeypatch.setattr(updates.sys, "frozen", True, raising=False)
    with pytest.raises(updates.UpdateError, match="Packaged"):
        updates.source_root()


def test_nested_folder_is_not_the_root(repositories):
    _, local = repositories
    nested = local / "nested"
    nested.mkdir()
    (nested / "Memoria.pyw").write_text("", encoding="utf-8")
    with pytest.raises(updates.UpdateError, match="source checkout"):
        updates.check(nested)


def test_missing_git_and_git_timeout(repositories, monkeypatch):
    _, local = repositories

    def missing(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(updates.subprocess, "run", missing)
    with pytest.raises(updates.UpdateError, match="Git was not found"):
        updates.check(local)

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("git", 90)

    monkeypatch.setattr(updates.subprocess, "run", timeout)
    with pytest.raises(updates.UpdateError, match="timed out"):
        updates.check(local)


def test_missing_venv_is_not_replaced_by_global_python(repositories):
    _, local = repositories
    with pytest.raises(updates.UpdateError, match=r"managed \.venv"):
        updates._managed_environment(local)


def test_remote_errors_are_redacted_and_noninteractive(repositories, monkeypatch):
    _, local = repositories
    seen = {}

    def failure(command, **kwargs):
        seen.update(command=command, **kwargs)
        return subprocess.CompletedProcess(
            command, 128, "", "fatal: unable to fetch https://alice:secret@example.invalid/repo",
        )

    monkeypatch.setattr(updates.subprocess, "run", failure)
    with pytest.raises(updates.UpdateError) as error:
        updates._git(local, "fetch", "team")
    assert "secret" not in str(error.value)
    assert "alice" not in str(error.value)
    assert isinstance(seen["command"], list)
    assert seen["stdin"] == subprocess.DEVNULL
    assert seen["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert seen["env"]["GCM_INTERACTIVE"] == "Never"
    assert "BatchMode=yes" in seen["env"]["GIT_SSH_COMMAND"]
    assert seen["timeout"] == updates.GIT_TIMEOUT


def test_fast_forward_only_to_approved_commit(approved, managed, progress):
    _, local, info = approved
    calls = []
    hook = local / ".git" / "hooks" / "post-merge"
    hook.write_text("#!/bin/sh\ntouch hook-was-run\n", encoding="utf-8")
    hook.chmod(stat.S_IRWXU)
    environment = updates._apply_update(info, progress)
    assert environment == managed
    assert git(local, "rev-parse", "HEAD") == info.remote_head
    assert (local / "feature.txt").is_file()
    assert not (local / "hook-was-run").exists()
    assert not (local / ".git" / "memoria-update.lock").exists()
    assert git(local, "status", "--porcelain") == ""
    assert not calls


@pytest.mark.parametrize("race", ["head", "branch", "upstream", "remote", "dirty", "target"])
def test_races_require_a_new_check(approved, managed, progress, race):
    upstream, local, info = approved
    if race == "head":
        commit(local, "local.txt", "new local commit")
    elif race == "branch":
        git(local, "checkout", "--quiet", "-b", "other", "--track", "team/release-line")
    elif race == "upstream":
        git(local, "config", "branch.release-line.merge", "refs/heads/another")
    elif race == "remote":
        git(local, "remote", "set-url", "team", str(upstream.parent / "other remote"))
    elif race == "dirty":
        (local / "not-committed.txt").write_text("keep me", encoding="utf-8")
    else:
        commit(upstream, "later.txt", "upstream moved")
    previous_head = git(local, "rev-parse", "HEAD")
    with pytest.raises(updates.UpdateError):
        updates._apply_update(info, progress)
    assert git(local, "rev-parse", "HEAD") == previous_head
    assert not (local / "feature.txt").exists()
    assert not (local / ".git" / "memoria-update.lock").exists()


def test_update_lock_conflict_preserves_existing_lock(approved, managed, progress):
    _, local, info = approved
    lock = local / ".git" / "memoria-update.lock"
    lock.write_text("someone else's updater", encoding="utf-8")
    with pytest.raises(updates.UpdateError, match="Another updater"):
        updates._apply_update(info, progress)
    assert lock.read_text(encoding="utf-8") == "someone else's updater"
    assert git(local, "rev-parse", "HEAD") == info.local_head


def test_ignored_collision_is_not_overwritten(repositories, managed, progress):
    upstream, local = repositories
    (upstream / "ignored.txt").write_text("upstream", encoding="utf-8")
    git(upstream, "add", "--force", "ignored.txt")
    git(upstream, "commit", "--quiet", "-m", "new tracked file")
    (local / "ignored.txt").write_text("private ignored content", encoding="utf-8")
    info = updates.check(local)
    assert info.can_update
    with pytest.raises(updates.UpdateError, match="merge failed"):
        updates._apply_update(info, progress)
    assert (local / "ignored.txt").read_text(encoding="utf-8") == "private ignored content"
    assert git(local, "rev-parse", "HEAD") == info.local_head


def test_changed_dependencies_use_managed_pip_with_separate_arguments(
    repositories, managed, progress, monkeypatch,
):
    upstream, local = repositories
    commit(upstream, "requirements.txt", "example-package>=2\n")
    info = updates.check(local)
    commands = []
    monkeypatch.setattr(
        updates, "_stream_command", lambda command, repo, logger: commands.append((command, repo)),
    )
    updates._apply_update(info, progress)
    assert info.changed_manifests == ("requirements.txt",)
    assert len(commands) == 1
    command, repo = commands[0]
    assert command[:4] == [str(managed.python), "-I", "-m", "pip"]
    assert command[command.index("-r") + 1] == str(local / "requirements.txt")
    assert command[command.index("--prefix") + 1] == str(local / ".venv")
    assert "--no-user" in command
    assert "--upgrade" not in command
    assert repo == local
    assert git(local, "rev-parse", "HEAD") == info.remote_head


def test_pyproject_dependencies_are_installed_without_editable_checkout(
    repositories, managed, progress, monkeypatch,
):
    upstream, local = repositories
    commit(
        upstream, "pyproject.toml",
        '[project]\nrequires-python=">=3.11,<4"\ndependencies=["new-package>=2", "other; os_name == \'nt\'"]\n',
    )
    info = updates.check(local)
    commands = []
    monkeypatch.setattr(updates, "_stream_command", lambda command, *_: commands.append(command))
    updates._apply_update(info, progress)
    assert "new-package>=2" in commands[0]
    assert "other; os_name == 'nt'" in commands[0]
    assert "-e" not in commands[0]


@pytest.mark.parametrize("content, message", [
    ("[project\n", "Invalid pyproject"),
    ('[project]\nrequires-python=">=99"\n', "requires Python"),
    ('[project]\ndependencies="-r steal.txt"\n', "Invalid project.dependencies"),
    ('[project]\ndependencies=["--target=elsewhere"]\n', "Invalid project.dependencies"),
    ('[project]\ndynamic=["dependencies"]\n', "Dynamic project dependencies"),
    ('[project]\nrequires-python=">=3.11rc1"\n', "Cannot safely evaluate"),
])
def test_invalid_or_unsupported_manifest_blocks_merge(
    repositories, managed, progress, content, message,
):
    upstream, local = repositories
    commit(upstream, "pyproject.toml", content)
    info = updates.check(local)
    with pytest.raises(updates.UpdateError, match=message):
        updates._apply_update(info, progress)
    assert git(local, "rev-parse", "HEAD") == info.local_head


def test_removed_manifest_requires_manual_migration(repositories, managed, progress):
    upstream, local = repositories
    git(upstream, "rm", "requirements.txt")
    git(upstream, "commit", "--quiet", "-m", "remove manifest")
    info = updates.check(local)
    with pytest.raises(updates.UpdateError, match="manifest removed"):
        updates._apply_update(info, progress)
    assert (local / "requirements.txt").is_file()
    assert git(local, "rev-parse", "HEAD") == info.local_head


def test_removed_launcher_requires_manual_migration(repositories, managed, progress):
    upstream, local = repositories
    git(upstream, "rm", "Memoria.pyw")
    git(upstream, "commit", "--quiet", "-m", "remove launcher")
    info = updates.check(local)
    with pytest.raises(updates.UpdateError, match="application launcher"):
        updates._apply_update(info, progress)
    assert (local / "Memoria.pyw").is_file()
    assert git(local, "rev-parse", "HEAD") == info.local_head


@pytest.mark.parametrize("requirement, version, expected", [
    (">=3.11,<4", (3, 12, 10), True),
    (">=3.13", (3, 12, 10), False),
    ("~=3.11", (3, 12, 0), True),
    ("~=3.11.2", (3, 12, 0), False),
    ("==3.12.*", (3, 12, 10), True),
    ("!=3.12.*", (3, 12, 10), False),
    (">=3.11,!=3.12.10", (3, 12, 10), False),
])
def test_python_requirements(requirement, version, expected):
    assert updates._supports_python(requirement, version) is expected


def test_installer_failure_is_persistent_and_blocks_restart(
    repositories, managed, progress, monkeypatch,
):
    upstream, local = repositories
    commit(upstream, "requirements.txt", "changed-package\n")
    info = updates.check(local)
    path = request_file(info, progress)
    monkeypatch.setattr(updates, "_wait_for_parent", lambda *_: None)
    monkeypatch.setattr(updates, "_restart", lambda *_: pytest.fail("must not restart"))

    def fail_install(*_):
        raise updates.UpdateError("dependency installation failed")

    monkeypatch.setattr(updates, "_stream_command", fail_install)
    assert updates._run_helper(path) == "failed"
    result = json.loads((progress.directory / "result.json").read_text(encoding="utf-8"))
    assert result["phase"] == "failed"
    assert result["failed_phase"] == "installing_dependencies"
    assert "dependency installation failed" in result["error"]
    assert "dependency installation failed" in (progress.directory / "update.log").read_text(
        encoding="utf-8",
    )
    assert git(local, "rev-parse", "HEAD") == info.remote_head


def test_helper_does_not_apply_until_parent_wait_finishes(approved, managed, progress, monkeypatch):
    _, _, info = approved
    path = request_file(info, progress)
    events = []
    monkeypatch.setattr(updates, "_wait_for_parent", lambda *_: events.append("parent-exited"))
    monkeypatch.setattr(
        updates, "_apply_update", lambda *_: events.append("apply") or managed,
    )
    monkeypatch.setattr(updates, "_restart", lambda *_: events.append("restart"))
    assert updates._run_helper(path) == "success"
    assert events == ["parent-exited", "apply", "restart"]


def test_helper_cancel_does_not_apply(approved, progress, monkeypatch):
    _, local, info = approved
    path = request_file(info, progress)
    (progress.directory / "cancel").touch()
    monkeypatch.setattr(updates, "_wait_for_parent", lambda *_: None)
    monkeypatch.setattr(updates, "_apply_update", lambda *_: pytest.fail("must not apply"))
    assert updates._run_helper(path) == "cancelled"
    assert git(local, "rev-parse", "HEAD") == info.local_head
    assert json.loads((progress.directory / "result.json").read_text())["phase"] == "cancelled"


@pytest.mark.parametrize("cancel", [True, False])
def test_ready_is_written_after_watching_exact_parent(progress, monkeypatch, cancel):
    events = []

    class Parent:
        def __init__(self, pid, creation):
            events.append(("watch", pid, creation))

        def exited(self):
            assert (progress.directory / "ready.json").is_file()
            events.append("exit-polled")
            return True

        def close(self):
            events.append("handle-closed")

    monkeypatch.setattr(updates, "_WindowsProcess", Parent)
    if cancel:
        (progress.directory / "cancel").touch()
        with pytest.raises(updates.UpdateError, match="cancelled"):
            updates._wait_for_parent({"parent_pid": 12, "parent_creation": 34}, progress.directory, progress)
        assert "exit-polled" not in events
    else:
        updates._wait_for_parent({"parent_pid": 12, "parent_creation": 34}, progress.directory, progress)
        assert "exit-polled" in events
    assert events[0] == ("watch", 12, 34)
    assert events[-1] == "handle-closed"


def test_parent_wait_times_out_without_apply(progress, monkeypatch):
    closed = []
    parent = SimpleNamespace(exited=lambda: False, close=lambda: closed.append(True))
    monkeypatch.setattr(updates, "_WindowsProcess", lambda *_: parent)
    monkeypatch.setattr(updates, "EXIT_TIMEOUT", 0)
    with pytest.raises(updates.UpdateError, match="No update was applied"):
        updates._wait_for_parent({"parent_pid": 1, "parent_creation": 2}, progress.directory, progress)
    assert closed == [True]


@pytest.mark.skipif(os.name != "nt", reason="Windows handle and console contract")
def test_windows_handle_rejects_recycled_process_id():
    handle = updates._WindowsProcess(os.getpid())
    try:
        assert not handle.exited()
        with pytest.raises(updates.UpdateError, match="process changed"):
            updates._WindowsProcess(os.getpid(), handle.creation + 1)
    finally:
        handle.close()


@pytest.mark.skipif(os.name != "nt", reason="Windows console launch contract")
def test_launch_snapshots_outside_repo_without_sensitive_urls(
    approved, managed, tmp_path, monkeypatch,
):
    _, local, info = approved
    captured = {}
    monkeypatch.setattr(updates, "_updates_root", lambda: tmp_path / "device updates")
    monkeypatch.setenv("MEMORIA_PROFILE", "isolated-profile")
    real_popen = updates.subprocess.Popen

    def launch(command, **kwargs):
        if command[0] == "git":
            return real_popen(command, **kwargs)
        captured.update(command=command, **kwargs)
        return SimpleNamespace(pid=987)

    monkeypatch.setattr(updates.subprocess, "Popen", launch)
    handoff = updates.launch_update(info)
    try:
        assert handoff.pid == 987
        assert not handoff.directory.is_relative_to(local)
        assert not handoff.ready.exists()
        helper = handoff.directory / "helper.py"
        request = handoff.directory / "request.json"
        assert helper.read_bytes() == Path(updates.__file__).read_bytes()
        assert captured["command"] == [str(managed.python), "-I", str(helper), str(request)]
        assert captured["creationflags"] == subprocess.CREATE_NEW_CONSOLE
        assert captured["env"]["MEMORIA_PROFILE"] == "isolated-profile"
        data = json.loads(request.read_text(encoding="utf-8"))
        assert data["approved"]["remote_head"] == info.remote_head
        assert data["parent_pid"] == os.getpid()
        assert "url" not in data["approved"]
        assert data["approved"]["remote_fingerprint"]
    finally:
        for path in handoff.directory.iterdir():
            path.chmod(stat.S_IWRITE | stat.S_IREAD)


def test_restart_requires_readiness_not_just_spawn(approved, managed, progress, monkeypatch):
    _, local, info = approved
    captured = {}
    monkeypatch.setattr(updates, "STARTUP_TIMEOUT", 0)

    def launch(command, **kwargs):
        captured.update(command=command, **kwargs)
        return SimpleNamespace(pid=78, poll=lambda: None)

    monkeypatch.setattr(updates.subprocess, "Popen", launch)
    with pytest.raises(updates.UpdateError, match="did not confirm startup"):
        updates._restart(info, managed, progress)
    assert captured["command"] == [str(managed.pythonw), str(local / "Memoria.pyw")]
    assert captured["cwd"] == str(local)
    assert captured["env"]["MEMORIA_UPDATE_READY"].startswith(str(progress.directory))
    assert json.loads((progress.directory / "result.json").read_text())["phase"] != "success"


def test_restart_success_requires_marker_and_living_process(approved, managed, progress, monkeypatch):
    _, _, info = approved

    def launch(command, **kwargs):
        Path(kwargs["env"]["MEMORIA_UPDATE_READY"]).write_text("ready", encoding="utf-8")
        return SimpleNamespace(pid=78, poll=lambda: None)

    monkeypatch.setattr(updates.subprocess, "Popen", launch)
    updates._restart(info, managed, progress)
    assert json.loads((progress.directory / "result.json").read_text())["phase"] == "success"
    monkeypatch.setattr(
        updates.subprocess, "Popen", lambda *_, **__: SimpleNamespace(pid=79, poll=lambda: 1),
    )
    with pytest.raises(updates.UpdateError, match="exited before becoming ready"):
        updates._restart(info, managed, progress)


def test_mark_restart_ready_is_exclusive_and_consumes_env(tmp_path, monkeypatch):
    root = tmp_path / "device updates"
    directory = root / ("a" * 32)
    directory.mkdir(parents=True)
    path = directory / ("startup-" + "b" * 32 + ".ready")
    monkeypatch.setattr(updates, "_updates_root", lambda: root)
    monkeypatch.setenv("MEMORIA_UPDATE_READY", str(path))
    updates.mark_restart_ready()
    assert json.loads(path.read_text(encoding="utf-8"))["pid"] == os.getpid()
    assert "MEMORIA_UPDATE_READY" not in os.environ
    updates.mark_restart_ready()
    original = path.read_bytes()
    monkeypatch.setenv("MEMORIA_UPDATE_READY", str(path))
    with pytest.raises(updates.UpdateError, match="Unable to confirm"):
        updates.mark_restart_ready()
    assert path.read_bytes() == original


def test_mark_restart_ready_cannot_overwrite_arbitrary_path(tmp_path, monkeypatch):
    path = tmp_path / "important.txt"
    path.write_text("keep me", encoding="utf-8")
    monkeypatch.setenv("MEMORIA_UPDATE_READY", str(path))
    with pytest.raises(updates.UpdateError, match="not in Memoria"):
        updates.mark_restart_ready()
    assert path.read_text(encoding="utf-8") == "keep me"
    assert "MEMORIA_UPDATE_READY" not in os.environ


def test_python_environment_disables_global_install_overrides(monkeypatch):
    monkeypatch.setenv("PIP_TARGET", "outside")
    monkeypatch.setenv("PIP_PREFIX", "outside")
    monkeypatch.setenv("PIP_USER", "yes")
    monkeypatch.setenv("PYTHONPATH", "outside")
    monkeypatch.setenv("MEMORIA_PROFILE", "my-profile")
    env = updates._python_environment()
    assert not {"PIP_TARGET", "PIP_PREFIX", "PIP_USER", "PYTHONPATH"} & env.keys()
    assert env["PIP_CONFIG_FILE"] == os.devnull
    assert env["PIP_REQUIRE_VIRTUALENV"] == "true"
    assert env["MEMORIA_PROFILE"] == "my-profile"
