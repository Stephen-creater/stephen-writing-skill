"""算一篇文章里 Stephen 改了多少，并记一行账。

这是最便宜也最真实的信号：不用开任何 Agent，日常写稿发布后跑一次就行。
攒够十几条，就能看出 Skill 到底有没有让初稿更接近发布版。

  python3 edit_ratio.py 初稿.md 发布版.md --title "豆包工作"

输出三个数，追加到 <日课创作>/work/改稿记录.jsonl（不进 Git）：
- 初稿被删掉的比例：初稿里有多少字没进发布版
- 发布版已写到的比例：发布版里有多少字初稿已经写出来了，越高你越省事
- 长度比：发布版字数 ÷ 初稿字数

用 `--show` 看历史。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
LOG = SKILL.parent / "work" / "改稿记录.jsonl"


def units(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|```.*?```", "", text, flags=re.S)
    return "".join(ch for ch in text if ch.isalnum())


def overlap(source: str, target: str, k: int = 8) -> float:
    grams = {source[i:i + k] for i in range(len(source) - k + 1)}
    hit = [False] * len(target)
    for i in range(len(target) - k + 1):
        if target[i:i + k] in grams:
            hit[i:i + k] = [True] * k
    return sum(hit) / max(1, len(target))


def show() -> None:
    if not LOG.exists():
        print("还没有记录")
        return
    rows = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        print(f"{row['标题']}：删掉 {row['初稿被删']:.0%}，发布版已写到 {row['发布版已写到']:.0%}，长度比 {row['长度比']:.2f}")
    if len(rows) > 1:
        cut = sum(r["初稿被删"] for r in rows) / len(rows)
        keep = sum(r["发布版已写到"] for r in rows) / len(rows)
        print(f"共 {len(rows)} 篇，平均删掉 {cut:.0%}，发布版平均已写到 {keep:.0%}")


def main() -> None:
    parser = argparse.ArgumentParser(description="算初稿到发布版改了多少")
    parser.add_argument("draft", nargs="?", type=Path)
    parser.add_argument("final", nargs="?", type=Path)
    parser.add_argument("--title", default="")
    parser.add_argument("--show", action="store_true", help="只看历史记录")
    args = parser.parse_args()

    if args.show or not args.draft:
        show()
        return
    if not args.final:
        raise SystemExit("要给两个文件：初稿和发布版")

    draft, final = units(args.draft), units(args.final)
    row = {
        "标题": args.title or args.final.stem,
        "初稿字数": len(draft),
        "发布版字数": len(final),
        "初稿被删": round(1 - overlap(final, draft), 3),
        "发布版已写到": round(overlap(draft, final), 3),
        "长度比": round(len(final) / max(1, len(draft)), 3),
        "初稿": str(args.draft),
        "发布版": str(args.final),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{row['标题']}：初稿 {row['初稿字数']} 字，发布版 {row['发布版字数']} 字，"
          f"删掉 {row['初稿被删']:.0%}，发布版已写到 {row['发布版已写到']:.0%}。记到 {LOG}")


if __name__ == "__main__":
    main()
