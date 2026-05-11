"""placeholderize.py - 把 HuaSan-LifeOS 占位符化生成 lifeos-template/"""
from __future__ import annotations
import shutil
import sys
from pathlib import Path


def run(config: dict) -> None:
    """主入口：按配置占位符化。"""
    src = Path(config["source_vault"]).resolve()
    tgt = Path(config["target_vault"]).resolve()

    # 1. 清空目标（保留 .git 如果存在）
    _clean_target(tgt)

    # 2. 全量 copy
    _copy_tree(src, tgt)

    # 3. 删除指定目录
    for d in config.get("delete_dirs", []):
        p = tgt / d
        if p.exists():
            shutil.rmtree(p)

    # 4. 删除指定文件
    for f in config.get("delete_files", []):
        p = tgt / f
        if p.exists():
            p.unlink()

    # 5. 清空指定文件（保留文件，置空内容）
    for f in config.get("clear_files", []):
        p = tgt / f
        if p.exists():
            p.write_text("")

    # 6. 字符串替换（全 vault 内 .md/.json/.yaml/.txt 文件）
    replacements = config.get("string_replacements", {})
    if replacements:
        _replace_strings(tgt, replacements)

    # 7. 精简 .obsidian/plugins
    keep_plugins = config.get("obsidian_plugins_keep", [])
    _filter_obsidian_plugins(tgt, keep_plugins)


def _clean_target(tgt: Path) -> None:
    """清空目标，保留 .git 目录。"""
    if not tgt.exists():
        tgt.mkdir(parents=True)
        return
    git_dir = tgt / ".git"
    git_backup = None
    if git_dir.exists():
        git_backup = tgt.parent / f".{tgt.name}.git.bak"
        shutil.move(str(git_dir), str(git_backup))
    for child in tgt.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    if git_backup:
        shutil.move(str(git_backup), str(git_dir))


def _copy_tree(src: Path, tgt: Path) -> None:
    """copy src into tgt, skipping .git."""
    for item in src.iterdir():
        if item.name == ".git":
            continue
        target = tgt / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns(".git"))
        else:
            shutil.copy2(item, target)


def _replace_strings(root: Path, replacements: dict) -> None:
    """在所有 .md/.json/.yaml/.txt 文件里做字符串替换。"""
    extensions = {".md", ".json", ".yaml", ".yml", ".txt", ".sh"}
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in extensions:
            continue
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            continue
        modified = text
        for old, new in replacements.items():
            modified = modified.replace(old, new)
        if modified != text:
            f.write_text(modified)


def _filter_obsidian_plugins(root: Path, keep: list) -> None:
    """精简 .obsidian/plugins/ 只保留 whitelist 里的插件。"""
    plugins_dir = root / ".obsidian" / "plugins"
    if not plugins_dir.exists():
        return
    for child in plugins_dir.iterdir():
        if child.is_dir() and child.name not in keep:
            shutil.rmtree(child)


if __name__ == "__main__":
    import yaml
    config_path = sys.argv[1] if len(sys.argv) > 1 else "placeholder-config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    run(config)
    print(f"✅ Generated: {config['target_vault']}")
