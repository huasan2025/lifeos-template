"""Tests for placeholderize.py"""
import os
import shutil
import tempfile
from pathlib import Path
import pytest

import placeholderize


@pytest.fixture
def tmp_vault():
    """Create a temp source vault with minimal structure."""
    src = tempfile.mkdtemp(prefix="src_vault_")
    Path(src, "CLAUDE.md").write_text("画伞是 yangfan，沉舟是助理。Vault 是 HuaSan-LifeOS。")
    Path(src, "02-Problems").mkdir()
    Path(src, "02-Problems", "real-problem.md").write_text("画伞的核心问题")
    Path(src, "03-Projects").mkdir()
    Path(src, "03-Projects", "delete-me").mkdir()
    Path(src, "03-Projects", "delete-me", "x.md").write_text("delete me")
    yield src
    shutil.rmtree(src)


@pytest.fixture
def tmp_target():
    """Create a temp target dir, return its path."""
    tgt = tempfile.mkdtemp(prefix="tgt_vault_")
    yield tgt
    shutil.rmtree(tgt)


def test_replace_strings_in_file(tmp_vault, tmp_target):
    """Verify string replacement runs on all .md files."""
    config = {
        "source_vault": tmp_vault,
        "target_vault": tmp_target,
        "string_replacements": {"画伞": "${USER_NAME}", "沉舟": "${ASSISTANT_NAME}", "HuaSan-LifeOS": "${VAULT_NAME}", "yangfan": "${USER_NAME}"},
        "delete_dirs": [],
        "delete_files": [],
        "clear_files": [],
        "obsidian_plugins_keep": [],
    }
    placeholderize.run(config)
    out = Path(tmp_target, "CLAUDE.md").read_text()
    assert "画伞" not in out
    assert "沉舟" not in out
    assert "${USER_NAME}" in out
    assert "${ASSISTANT_NAME}" in out
    assert "${VAULT_NAME}" in out


def test_delete_dirs(tmp_vault, tmp_target):
    config = {
        "source_vault": tmp_vault,
        "target_vault": tmp_target,
        "string_replacements": {},
        "delete_dirs": ["03-Projects/delete-me"],
        "delete_files": [],
        "clear_files": [],
        "obsidian_plugins_keep": [],
    }
    placeholderize.run(config)
    assert not (Path(tmp_target) / "03-Projects" / "delete-me").exists()
    assert (Path(tmp_target) / "03-Projects").exists()


def test_delete_files(tmp_vault, tmp_target):
    config = {
        "source_vault": tmp_vault,
        "target_vault": tmp_target,
        "string_replacements": {},
        "delete_dirs": [],
        "delete_files": ["02-Problems/real-problem.md"],
        "clear_files": [],
        "obsidian_plugins_keep": [],
    }
    placeholderize.run(config)
    assert not (Path(tmp_target) / "02-Problems" / "real-problem.md").exists()


def test_clear_files(tmp_vault, tmp_target):
    Path(tmp_vault, "PROGRESS.md").write_text("画伞 todo list")
    config = {
        "source_vault": tmp_vault,
        "target_vault": tmp_target,
        "string_replacements": {},
        "delete_dirs": [],
        "delete_files": [],
        "clear_files": ["PROGRESS.md"],
        "obsidian_plugins_keep": [],
    }
    placeholderize.run(config)
    out = Path(tmp_target, "PROGRESS.md").read_text()
    assert out == ""


def test_preserve_git(tmp_vault, tmp_target):
    """target dir's .git should be preserved if exists."""
    git_dir = Path(tmp_target, ".git")
    git_dir.mkdir()
    Path(git_dir, "HEAD").write_text("ref: refs/heads/main")
    config = {
        "source_vault": tmp_vault,
        "target_vault": tmp_target,
        "string_replacements": {},
        "delete_dirs": [],
        "delete_files": [],
        "clear_files": [],
        "obsidian_plugins_keep": [],
    }
    placeholderize.run(config)
    assert Path(tmp_target, ".git", "HEAD").exists()
