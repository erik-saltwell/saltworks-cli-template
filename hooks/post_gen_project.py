from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True)


def run_capture(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def should_init_local_git_repo() -> bool:
    """
    Only init git if it won't create a nested repo.
    - If .git exists in the generated project dir: already a repo.
    - If parent has .git: generated inside an existing repo -> don't init.
    """
    if Path(".git").exists():
        return False
    if (Path.cwd().parent / ".git").exists():
        return False
    return True


def ensure_git_identity(author_name: str, email: str) -> None:
    # Set local identity only if missing
    name = run_capture(["git", "config", "user.name"]).stdout.strip()
    if not name and author_name:
        run(["git", "config", "user.name", author_name])

    mail = run_capture(["git", "config", "user.email"]).stdout.strip()
    if not mail and email:
        run(["git", "config", "user.email", email])


def copy_env_example_to_env() -> None:
    example = Path(".env.example")
    env = Path(".env")
    # Create a local .env for convenience; keep it uncommitted.
    if example.exists() and not env.exists():
        shutil.copyfile(example, env)


def ensure_uv_env_and_deps() -> bool:
    """
    Create venv and sync deps. Returns True if uv is available and commands ran.
    """
    if shutil.which("uv") is None:
        print("WARN: 'uv' not found on PATH; skipping 'uv venv' and 'uv sync'.")
        return False

    # Create project venv
    run(["uv", "venv"])
    # Install deps into .venv (uses existing uv.lock/pyproject)
    run(["uv", "sync"])
    return True


def install_precommit_hooks_only_for_local_repo(uv_ok: bool, local_git_repo: bool) -> None:
    """
    Install hooks only when we have:
    - a local .git (we initialized it here), and
    - uv ran successfully (so pre-commit is available via uv run)
    This avoids accidentally installing into a parent repo.
    """
    if not (uv_ok and local_git_repo):
        return

    # pre-commit installs hooks into .git/hooks
    run(["uv", "run", "pre-commit", "install"])


# 1) Always create .env from .env.example (but it remains uncommitted due to .gitignore)
copy_env_example_to_env()

# 2) Git init + first commit (only if safe, and git exists)
local_git_repo = False
if shutil.which("git") is not None and should_init_local_git_repo():
    # Prefer `git init -b main` when available
    r = subprocess.run(["git", "init", "-b", "main"], text=True)
    if r.returncode != 0:
        run(["git", "init"])
        subprocess.run(["git", "branch", "-M", "main"], text=True)

    local_git_repo = True

    ensure_git_identity(
        author_name="{{ cookiecutter.author_name }}",
        email="{{ cookiecutter.author_email }}",
    )

    run(["git", "add", "-A"])

    # Avoid failure if user globally requires signed commits
    commit = run_capture(["git", "commit", "-m", "Initial scaffold", "--no-gpg-sign"], check=False)
    if commit.returncode != 0:
        msg = (commit.stderr or commit.stdout).strip().lower()
        if "nothing to commit" not in msg:
            raise RuntimeError(commit.stderr or commit.stdout)

# 3) uv venv + uv sync (you asked for this)
uv_ok = ensure_uv_env_and_deps()

# 4) pre-commit install (automated)
install_precommit_hooks_only_for_local_repo(uv_ok=uv_ok, local_git_repo=local_git_repo)
