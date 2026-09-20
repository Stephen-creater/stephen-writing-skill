"""把一篇已发布的文章加进评测题库。

需要四样东西：当时的要求和材料（save_materials.py 存的）、Agent 初稿、Stephen 的发布版。
发布版先用 `python3 scripts/sync_published.py` 从飞书同步到 已发布文章/。

  python3 add_case.py doubao \
      --materials "<日课创作>/work/材料/豆包工作" \
      --draft "<日课创作>/work/doubao-work-feishu-guide-draft.md" \
      --final "<日课创作>/已发布文章/第五周__8.26 字节「豆包工作」重磅发布.md" \
      --category AI热点与产品发布 [--example "AI热点与产品发布/8.26 ....md"] [--split dev]

新题默认进留出集（holdout），因为它没参与过改规则。加完记得重新跑一遍评测基线。
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
CASES = SKILL.parent / "评测" / "题库"
CATEGORIES = ("AI热点与产品发布", "产品实测与主观评测", "概念与方法论拆解", "实践指南与避坑")


def main() -> None:
    parser = argparse.ArgumentParser(description="把一篇已发布文章加进评测题库")
    parser.add_argument("case_id", help="题目代号，英文小写加连字符")
    parser.add_argument("--materials", required=True, type=Path, help="save_materials.py 存的那个目录")
    parser.add_argument("--draft", type=Path, help="当时的 Agent 初稿，用来校准评委，可以不给")
    parser.add_argument("--final", required=True, type=Path, help="Stephen 的发布版")
    parser.add_argument("--category", required=True, choices=CATEGORIES)
    parser.add_argument("--example", help="这篇在范文库里的路径（分类/文件名.md），有就填，评测时会临时删掉它")
    parser.add_argument("--split", default="holdout", choices=["dev", "holdout"])
    args = parser.parse_args()

    brief = args.materials / "要求.md"
    sources = sorted((args.materials / "材料").glob("*")) if (args.materials / "材料").is_dir() else []
    if not brief.is_file() or not sources:
        raise SystemExit(f"{args.materials} 里缺要求.md 或材料，先用 save_materials.py 存")
    if not args.final.is_file():
        raise SystemExit(f"找不到发布版：{args.final}")

    out = CASES / args.case_id
    (out / "材料").mkdir(parents=True, exist_ok=True)
    shutil.copy(brief, out / "要求.md")
    for index, path in enumerate(sources, start=1):
        shutil.copy(path, out / "材料" / f"材料{index}{path.suffix or '.md'}")
    shutil.copy(args.final, out / "定稿.md")
    if args.draft and args.draft.is_file():
        shutil.copy(args.draft, out / "历史初稿.md")

    meta = {
        "id": args.case_id,
        "split": args.split,
        "cat": args.category,
        "example": args.example,
        "final_source": str(args.final),
        "material_chars": [len(p.read_text(encoding="utf-8", errors="ignore")) for p in sources],
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    total = len(list(CASES.glob("*/meta.json")))
    print(f"已加入题库：{out}（{args.split}）。题库现在有 {total} 道")
    print("接下来：跑一次 eval_writing.py prepare/pairs/score，给当前版本补上这道题的成绩")


if __name__ == "__main__":
    main()
