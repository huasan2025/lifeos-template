import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills_doctor import build_plan, execute_plan


def write_skill(root: Path, name: str, description: str = "test skill") -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n",
        encoding="utf-8",
    )
    return skill_dir


class SkillsDoctorTests(unittest.TestCase):
    def test_build_plan_flags_invalid_entries_and_missing_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agents = tmp_path / "agents"
            codex = tmp_path / "codex"
            agents.mkdir()
            codex.mkdir()

            write_skill(agents, "ill")
            write_skill(agents, "find-skills")
            (agents / "notes.md").write_text("not a skill", encoding="utf-8")

            os.symlink(agents / "ill", codex / "ill")
            os.symlink(tmp_path / "missing-target", codex / "broken-skill")
            (codex / "find-skills alias").write_text("alias", encoding="utf-8")
            (codex / "notebooklm.md").write_text("junk", encoding="utf-8")

            plan = build_plan(agents, codex, tmp_path / "quarantine")

            canonical = {item.name for item in plan["canonical_skills"]}
            self.assertEqual(canonical, {"find-skills", "ill"})

            actions = {(item["kind"], item["name"]) for item in plan["actions"]}
            self.assertIn(("create_symlink", "find-skills"), actions)
            self.assertIn(("quarantine_broken_symlink", "broken-skill"), actions)
            self.assertIn(("quarantine_file", "find-skills alias"), actions)
            self.assertIn(("quarantine_file", "notebooklm.md"), actions)
            self.assertIn(("quarantine_canonical_file", "notes.md"), actions)

            issues = {(issue["severity"], issue["name"]) for issue in plan["issues"]}
            self.assertIn(("error", "broken-skill"), issues)
            self.assertIn(("warn", "notes.md"), issues)

    def test_fix_replaces_duplicate_directory_with_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agents = tmp_path / "agents"
            codex = tmp_path / "codex"
            quarantine = tmp_path / "quarantine"
            agents.mkdir()
            codex.mkdir()

            source = write_skill(agents, "feishu-lark-agent")
            (source / "tool.py").write_text("print('ok')\n", encoding="utf-8")

            duplicate = codex / "feishu-lark-agent"
            duplicate.mkdir()
            (duplicate / "SKILL.md").write_text(
                (source / "SKILL.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (duplicate / "tool.py").write_text("print('ok')\n", encoding="utf-8")

            plan = build_plan(agents, codex, quarantine)
            execute_plan(plan["actions"], quarantine, dry_run=False)

            self.assertTrue((codex / "feishu-lark-agent").is_symlink())
            self.assertEqual((codex / "feishu-lark-agent").resolve(), source.resolve())
            moved = list(quarantine.glob("feishu-lark-agent*"))
            self.assertTrue(moved)


if __name__ == "__main__":
    unittest.main()
