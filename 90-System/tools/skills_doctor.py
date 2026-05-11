#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SkillEntry:
    name: str
    path: Path
    kind: str


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def is_skill_container(path: Path) -> bool:
    if not path.is_dir():
        return False
    for child in path.iterdir():
        if child.name.startswith("."):
            continue
        if is_skill_dir(child):
            return True
    return False


def discover_canonical_skills(root: Path) -> tuple[list[SkillEntry], list[dict]]:
    skills: list[SkillEntry] = []
    issues: list[dict] = []
    if not root.exists():
        issues.append({"severity": "error", "name": str(root), "message": "canonical root missing"})
        return skills, issues
    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if entry.name.startswith("."):
            continue
        if is_skill_dir(entry):
            skills.append(SkillEntry(entry.name, entry, "skill"))
            continue
        if is_skill_container(entry):
            skills.append(SkillEntry(entry.name, entry, "container"))
            continue
        issues.append(
            {
                "severity": "warn",
                "name": entry.name,
                "message": "non-skill entry in canonical root",
            }
        )
        actions = {
            "kind": "quarantine_canonical_file" if entry.is_file() else "quarantine_canonical_directory",
            "name": entry.name,
            "target": str(entry),
        }
        issues[-1]["action"] = actions["kind"]
        skills.append(SkillEntry(entry.name, entry, "invalid"))
    return skills, issues


def trees_identical(left: Path, right: Path) -> bool:
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.funny_files:
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(
        left,
        right,
        comparison.common_files,
        shallow=False,
    )
    if mismatch or errors:
        return False
    return all(
        trees_identical(left / common_dir, right / common_dir)
        for common_dir in comparison.common_dirs
    )


def quarantine_destination(quarantine_root: Path, name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return quarantine_root / f"{name}.{stamp}"


def build_plan(canonical_root: Path, mirror_root: Path, quarantine_root: Path) -> dict:
    discovered_entries, issues = discover_canonical_skills(canonical_root)
    canonical_skills = [entry for entry in discovered_entries if entry.kind in {"skill", "container"}]
    canonical_map = {skill.name: skill for skill in canonical_skills}
    actions: list[dict] = []
    for issue in issues:
        if "action" in issue:
            actions.append(
                {
                    "kind": issue["action"],
                    "name": issue["name"],
                    "target": str(canonical_root / issue["name"]),
                }
            )

    for skill in canonical_skills:
        mirror_path = mirror_root / skill.name
        if not mirror_path.exists() and not mirror_path.is_symlink():
            if skill.kind == "skill":
                actions.append(
                    {
                        "kind": "create_symlink",
                        "name": skill.name,
                        "source": str(skill.path),
                        "target": str(mirror_path),
                    }
                )
            continue

    for entry in sorted(mirror_root.iterdir(), key=lambda p: p.name):
        if entry.name.startswith("."):
            continue
        if entry.name == ".system":
            continue
        if entry.is_symlink() and not entry.exists():
            issues.append({"severity": "error", "name": entry.name, "message": "broken symlink in mirror root"})
            actions.append(
                {
                    "kind": "quarantine_broken_symlink",
                    "name": entry.name,
                    "target": str(entry),
                }
            )
            continue
        if entry.is_file():
            issues.append({"severity": "error", "name": entry.name, "message": "non-skill file in mirror root"})
            actions.append(
                {
                    "kind": "quarantine_file",
                    "name": entry.name,
                    "target": str(entry),
                }
            )
            if entry.name in canonical_map:
                actions.append(
                    {
                        "kind": "create_symlink",
                        "name": entry.name,
                        "source": str(canonical_map[entry.name].path),
                        "target": str(entry),
                    }
                )
            continue
        if entry.is_dir() and not entry.is_symlink():
            canonical = canonical_map.get(entry.name)
            if canonical and canonical.kind == "skill" and trees_identical(entry, canonical.path):
                issues.append({"severity": "warn", "name": entry.name, "message": "duplicate real directory in mirror root"})
                actions.append(
                    {
                        "kind": "replace_directory_with_symlink",
                        "name": entry.name,
                        "source": str(canonical.path),
                        "target": str(entry),
                    }
                )
            elif is_skill_dir(entry):
                issues.append({"severity": "warn", "name": entry.name, "message": "skill exists only in mirror root"})
            else:
                issues.append({"severity": "error", "name": entry.name, "message": "invalid directory in mirror root"})
                actions.append(
                    {
                        "kind": "quarantine_directory",
                        "name": entry.name,
                        "target": str(entry),
                    }
                )

    return {
        "canonical_root": str(canonical_root),
        "mirror_root": str(mirror_root),
        "quarantine_root": str(quarantine_root),
        "canonical_skills": canonical_skills,
        "issues": issues,
        "actions": dedupe_actions(actions),
    }


def dedupe_actions(actions: Iterable[dict]) -> list[dict]:
    seen: set[tuple] = set()
    deduped: list[dict] = []
    for action in actions:
        key = tuple(sorted(action.items()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(action)
    return deduped


def move_to_quarantine(target: Path, quarantine_root: Path) -> Path:
    quarantine_root.mkdir(parents=True, exist_ok=True)
    destination = quarantine_destination(quarantine_root, target.name)
    shutil.move(str(target), str(destination))
    return destination


def execute_plan(actions: Iterable[dict], quarantine_root: Path, dry_run: bool) -> list[str]:
    output: list[str] = []
    for action in actions:
        kind = action["kind"]
        if kind == "create_symlink":
            target = Path(action["target"])
            source = Path(action["source"])
            output.append(f"create_symlink {target} -> {source}")
            if dry_run:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                raise RuntimeError(f"refusing to overwrite existing path: {target}")
            os.symlink(source, target)
            continue

        if kind in {
            "quarantine_broken_symlink",
            "quarantine_file",
            "quarantine_directory",
            "quarantine_canonical_file",
            "quarantine_canonical_directory",
        }:
            target = Path(action["target"])
            output.append(f"{kind} {target}")
            if not dry_run:
                move_to_quarantine(target, quarantine_root)
            continue

        if kind == "replace_directory_with_symlink":
            target = Path(action["target"])
            source = Path(action["source"])
            output.append(f"replace_directory_with_symlink {target} -> {source}")
            if dry_run:
                continue
            move_to_quarantine(target, quarantine_root)
            os.symlink(source, target)
            continue

        raise RuntimeError(f"unknown action: {kind}")
    return output


def render_report(plan: dict) -> str:
    lines: list[str] = []
    lines.append(f"canonical_root: {plan['canonical_root']}")
    lines.append(f"mirror_root: {plan['mirror_root']}")
    lines.append("")
    lines.append("canonical skills:")
    for skill in plan["canonical_skills"]:
        lines.append(f"- {skill.name} ({skill.kind})")
    lines.append("")
    lines.append("issues:")
    for issue in plan["issues"]:
        lines.append(f"- {issue['severity']}: {issue['name']} - {issue['message']}")
    if not plan["issues"]:
        lines.append("- none")
    lines.append("")
    lines.append("actions:")
    for action in plan["actions"]:
        detail = action.get("source", action.get("target", ""))
        lines.append(f"- {action['kind']}: {action['name']} {detail}".rstrip())
    if not plan["actions"]:
        lines.append("- none")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose and repair Codex skill discovery roots.")
    parser.add_argument("command", choices=["check", "fix"])
    parser.add_argument(
        "--canonical-root",
        default=str(Path.home() / ".agents" / "skills"),
    )
    parser.add_argument(
        "--mirror-root",
        default=str(Path.home() / ".codex" / "skills"),
    )
    parser.add_argument(
        "--quarantine-root",
        default=str(Path.home() / "StagingToDelete" / datetime.now().strftime("%Y-%m") / "skills-cleanup"),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_plan(
        Path(args.canonical_root).expanduser(),
        Path(args.mirror_root).expanduser(),
        Path(args.quarantine_root).expanduser(),
    )
    print(render_report(plan))
    if args.command == "fix":
        print("")
        print("execution:")
        for line in execute_plan(plan["actions"], Path(args.quarantine_root).expanduser(), args.dry_run):
            print(f"- {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
