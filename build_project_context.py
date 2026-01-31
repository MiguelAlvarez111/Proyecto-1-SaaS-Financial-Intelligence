#!/usr/bin/env python3
"""
Generates PROJECT_CONTEXT.md with full source code for architecture review.
Excludes: .json, .csv, .env, __pycache__, .git, venv.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "PROJECT_CONTEXT.md"

EXCLUDE_DIRS = {"__pycache__", ".git", "venv", "env", ".env", "node_modules"}
EXCLUDE_FILES = {".env", "PROJECT_CONTEXT.md", "build_project_context.py"}
INCLUDE_EXT = (".py", ".txt", ".toml", ".sh")
INCLUDE_NAMES = ("requirements.txt",)

def should_include(p: Path) -> bool:
    if p.name in EXCLUDE_FILES:
        return False
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return False
    if p.suffix in (".json", ".csv"):
        return False
    if p.suffix in INCLUDE_EXT:
        return True
    if p.name in INCLUDE_NAMES:
        return True
    return False

def file_tree(dir_path: Path, prefix: str = "") -> list[str]:
    lines = []
    try:
        entries = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return lines
    for i, entry in enumerate(entries):
        if entry.name.startswith(".") and entry.name not in [".streamlit", ".gitignore"]:
            continue
        if entry.name in EXCLUDE_DIRS and entry.is_dir():
            continue
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + entry.name)
        if entry.is_dir() and entry.name not in EXCLUDE_DIRS:
            ext = "    " if is_last else "│   "
            lines.extend(file_tree(entry, prefix + ext))
    return lines

def main():
    rel_root = ROOT.name
    tree_lines = [rel_root + "/"] + file_tree(ROOT)
    tree_text = "\n".join(tree_lines)

    files_to_include = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and (not d.startswith(".") or d == ".streamlit")]
        for f in files:
            path = Path(root) / f
            if path == OUTPUT or path == Path(__file__).resolve():
                continue
            if should_include(path):
                try:
                    rel = path.relative_to(ROOT)
                except ValueError:
                    continue
                files_to_include.append((rel, path))

    files_to_include.sort(key=lambda x: (str(x[0]).replace("\\", "/"),))

    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write("# PROJECT CONTEXT — SaaS Financial Intelligence\n\n")
        out.write("Documento para revisión de arquitectura. Código fuente: .py, requirements.txt, .toml, .sh.\n")
        out.write("Excluidos: .json, .csv, .env, __pycache__, .git, venv.\n\n---\n\n")
        out.write("## Estructura del Proyecto (File Tree)\n\n```\n")
        out.write(tree_text)
        out.write("\n```\n\n---\n\n")

        for rel, abspath in files_to_include:
            rel_str = str(rel).replace("\\", "/")
            try:
                content = abspath.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"# Error reading file: {e}\n"
            lang = "python" if abspath.suffix == ".py" else "toml" if abspath.suffix == ".toml" else "bash" if abspath.suffix == ".sh" else "text"
            out.write(f"## Nombre del Archivo: {rel_str}\n\n")
            out.write(f"```{lang}\n")
            out.write(content)
            if content and not content.endswith("\n"):
                out.write("\n")
            out.write("```\n\n")

    print(f"Written: {OUTPUT}")

if __name__ == "__main__":
    main()
