from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def safe_title(title: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]', "-", title).strip(" .-")
    if not cleaned:
        raise ValueError("标题不能为空")
    return cleaned


def save_draft(title: str, source: Path, project_root: Path) -> Path:
    content = source.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("待存档文件为空")

    target_dir = project_root / "成稿" / datetime.now().strftime("%Y-%m")
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = safe_title(title)
    target = target_dir / f"{stem}.md"
    sequence = 2
    while target.exists():
        target = target_dir / f"{stem}-{sequence}.md"
        sequence += 1

    target.write_text(content + "\n", encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="将确认后的文章存入项目成稿目录")
    parser.add_argument("title")
    parser.add_argument("source", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    target = save_draft(args.title, args.source, args.project_root.resolve())
    print(target)


if __name__ == "__main__":
    main()
