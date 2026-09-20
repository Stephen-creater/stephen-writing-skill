"""把这次写稿用到的要求和材料原样存一份，存到 <日课创作>/work/材料/<文章名>/。

以后 Stephen 发布了这篇，就能用 add_case.py 把它加进评测题库。不存材料，这篇就没法用来评测。

用法（在任意目录，路径按脚本自身位置解析）：

  python3 save_materials.py "豆包工作" --brief "用我们的 skill 写初稿，2500 字以内" 源文件1.md 源文件2.txt
  python3 save_materials.py "豆包工作" --brief "..." --link https://example.com/a --link https://example.com/b

材料是链接时先把正文取下来存成文件再传进来，只有链接的话只会记下地址。
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
STORE = SKILL.parent / "work" / "材料"


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|\n]', "_", name).strip()[:80] or "未命名"


def main() -> None:
    parser = argparse.ArgumentParser(description="存档这次的要求和材料")
    parser.add_argument("title", help="文章名，和初稿文件名对得上就行")
    parser.add_argument("files", nargs="*", type=Path, help="材料文件")
    parser.add_argument("--brief", required=True, help="Stephen 这次的要求，原话")
    parser.add_argument("--link", action="append", default=[], help="材料链接，可以给多个")
    args = parser.parse_args()

    out = STORE / safe(args.title)
    (out / "材料").mkdir(parents=True, exist_ok=True)
    (out / "要求.md").write_text(args.brief.strip() + "\n", encoding="utf-8")

    saved = []
    for index, path in enumerate(args.files, start=1):
        if not path.is_file():
            raise SystemExit(f"找不到材料文件：{path}")
        target = out / "材料" / f"材料{index}{path.suffix or '.md'}"
        shutil.copy(path, target)
        saved.append(target.name)
    if args.link:
        (out / "材料" / "链接.txt").write_text("\n".join(args.link) + "\n", encoding="utf-8")
        saved.append("链接.txt")

    print(f"已存到 {out}：要求.md，材料 {len(saved)} 份（{'、'.join(saved) or '无'}）")
    if not saved:
        print("提示：没有存下任何材料正文，这篇以后进不了评测题库")


if __name__ == "__main__":
    main()
