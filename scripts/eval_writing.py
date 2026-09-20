"""写作 Skill 评测：保证每次改规则，文章只会更接近 Stephen 的发布版，不会越改越差。

题库、运行结果和打分都在父项目的 评测/ 目录，只在本机（含付费文章全文），不进 Git。
评测怎么设计、为什么这样设计，见 references/evaluation.md。

  prepare <版本名> [--ref 提交或标签] [--split dev|holdout|all] [--reuse-drafts 旧版本名]
      给每道题准备写作任务：复制这一版 Skill（去掉这道题自己的范文），写好 任务.md
      --reuse-drafts 会把旧版本那一轮的未审初稿复制过来：只改了审稿指南时用它，
      跳过最贵的起草环节，两版从同一篇未审初稿出发，差别只来自审稿，结果也更准
  pairs <旧版本> <新版本> [--split ...]
      生成盲评任务：两份初稿随机标成 A、B，每道题两位评委、位置互换
  calibrate
      生成评委校准任务：Stephen 发布版和历史 Agent 初稿放在一起，不告诉评委哪篇是谁写的
  score <评委结果.json>
      汇总盲评或校准结果，记入 评测/历史.jsonl，判断新版本能不能上线
  history
      查看历次评测
  restore <标签>
      月光宝盒：把 Skill 目录恢复成某个已通过评测的版本（只改工作区，确认后再提交）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.parse import quote

SKILL = Path(__file__).resolve().parents[1]
PROJECT = SKILL.parent
EVAL = PROJECT / "评测"
CASES = EVAL / "题库"
RUNS = EVAL / "运行"
HISTORY = EVAL / "历史.jsonl"

FLAGS = {
    "重复": "同一个意思换说法又讲一遍，或案例后面补总结",
    "视角": "该用我的地方退成旁观者（开发者、用户），或没有亲历却写成我实测",
    "看不懂": "术语没解释、这个那个找不到指向、依赖看不到的图、跳步",
    "顺序": "东西在读者遇到之前就出场，或段落之间接不上",
    "编造": "和材料矛盾，或虚构亲历、实测、采访、数据、引语",
    "开头慢": "开头铺垫两句以上才进入正题",
    "结尾空": "结尾复述全文、喊口号或临时拔高",
    "堆案例": "同一个判断用了两个以上同类案例",
    "AI腔": "引号破折号很多、不是X而是Y、值得注意的是这类套话",
    "漏重点": "Stephen 发布版里的核心内容，初稿里没有",
}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=PROJECT, capture_output=True, text=True, check=True).stdout.strip()


def load_cases(split: str = "all") -> list[dict]:
    cases = []
    for meta_path in sorted(CASES.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["dir"] = meta_path.parent
        if split in ("all", meta["split"]):
            cases.append(meta)
    if not cases:
        raise SystemExit(f"题库为空：{CASES}")
    return cases


def snapshot(ref: str | None, dest: Path) -> str:
    """复制一版 Skill。ref 为空时复制当前工作区（包括没提交的修改）。"""
    if dest.exists():
        shutil.rmtree(dest)
    if ref is None:
        shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        dirty = bool(git("status", "--porcelain", "--", SKILL.name))
        return git("rev-parse", "--short", "HEAD") + ("+未提交修改" if dirty else "")
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "skill.tar"
        subprocess.run(["git", "archive", "-o", str(archive), ref, SKILL.name], cwd=PROJECT, check=True)
        with tarfile.open(archive) as tar:
            tar.extractall(tmp, filter="data")
        shutil.copytree(Path(tmp) / SKILL.name, dest)
    return git("rev-parse", "--short", ref)


def hide_own_example(skill_copy: Path, example: str | None) -> None:
    """被测文章自己的范文不能留在 Skill 里，否则等于把答案给了写稿的 Agent。"""
    if not example:
        return
    target = skill_copy / "examples" / example
    if target.exists():
        target.unlink()
    stem = Path(example).stem
    marks = {stem, quote(stem), quote(stem, safe="")}
    for standards in skill_copy.glob("examples/*/standards.md"):
        lines = standards.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [line for line in lines if not any(mark in line for mark in marks)]
        standards.write_text("".join(kept), encoding="utf-8")


TASK = """# 写作任务（评测用）

Stephen 的要求：

> {brief}

材料：
{materials}

只使用这一份 Skill：`{skill}/SKILL.md`，按它的说明读需要的文件并完成写作。

交付：
- 正文写到 `{out}/初稿.md`（只放文章本身）
- 交付说明写到 `{out}/交付说明.md`

{reuse}评测规则：
- 除了上面列出的材料，不要读取 日课创作 目录下的 已发布文章/、评测/、work/、stephen-writing-skill/，也不要读 ~/.codex 或 ~/.claude 里其他版本的 Skill。
- 不联网。材料不够的地方按材料写，需要核实的事实写进交付说明。
- Skill 要求的步骤照做（包括它要求的审稿），只是不要问 Stephen 问题，按最合理的理解直接写完。
"""


def cmd_prepare(args: argparse.Namespace) -> None:
    run = RUNS / args.label
    run.mkdir(parents=True, exist_ok=True)
    base = run / "_skill"
    commit = snapshot(args.ref, base)
    tasks = []
    for case in load_cases(args.split):
        out = run / case["id"]
        out.mkdir(exist_ok=True)
        skill_copy = out / "skill"
        if skill_copy.exists():
            shutil.rmtree(skill_copy)
        shutil.copytree(base, skill_copy)
        hide_own_example(skill_copy, case.get("example"))
        reused = False
        if args.reuse_drafts:
            source = RUNS / args.reuse_drafts / case["id"] / "初稿-未审.md"
            if not source.exists():
                raise SystemExit(f"{args.reuse_drafts} 那一轮没有留下未审初稿：{source}")
            shutil.copy(source, out / "初稿-未审.md")
            reused = True
        materials = "\n".join(f"- `{p}`" for p in sorted((case["dir"] / "材料").glob("*.md")))
        brief = (case["dir"] / "要求.md").read_text(encoding="utf-8").strip()
        reuse_note = f"这道题的未审初稿已经写好，在 `{out}/初稿-未审.md`，直接从审稿那一步开始。\n\n" if reused else ""
        task = TASK.format(brief=brief, materials=materials, skill=skill_copy, out=out, reuse=reuse_note)
        (out / "任务.md").write_text(task, encoding="utf-8")
        tasks.append({"case": case["id"], "split": case["split"], "task": str(out / "任务.md"), "out": str(out), "起草": "复用 " + args.reuse_drafts if reused else "重跑"})
    manifest = {"label": args.label, "ref": args.ref or "工作区", "commit": commit, "复用未审初稿": args.reuse_drafts, "tasks": tasks}
    (run / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=1))


def order_for(case: str, a: str, b: str, judge: int) -> tuple[str, str]:
    first = int(hashlib.sha1(f"{case}|{a}|{b}".encode()).hexdigest(), 16) % 2 == 0
    if judge == 1:
        first = not first
    return (a, b) if first else (b, a)


def judge_packet(case: dict, left: Path, right: Path, labels: tuple[str, str], judge: int, with_reference: bool) -> dict:
    return {
        "case": case["id"],
        "split": case["split"],
        "judge": judge,
        "order": {"A": labels[0], "B": labels[1]},
        "brief": str(case["dir"] / "要求.md"),
        "reference": str(case["dir"] / "定稿.md") if with_reference else None,
        "materials": [str(p) for p in sorted((case["dir"] / "材料").glob("*.md"))],
        "A": str(left),
        "B": str(right),
    }


def cmd_pairs(args: argparse.Namespace) -> None:
    packets = []
    for case in load_cases(args.split):
        drafts = {label: RUNS / label / case["id"] / "初稿.md" for label in (args.old, args.new)}
        missing = [str(p) for p in drafts.values() if not p.exists()]
        if missing:
            print("缺少初稿，跳过：" + "，".join(missing), file=sys.stderr)
            continue
        for judge in (0, 1):
            first, second = order_for(case["id"], args.old, args.new, judge)
            packets.append(judge_packet(case, drafts[first], drafts[second], (first, second), judge, True))
    out = EVAL / f"对比-{args.old}-vs-{args.new}.json"
    out.write_text(json.dumps(packets, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(packets)} 个盲评任务：{out}")


def cmd_calibrate(args: argparse.Namespace) -> None:
    packets = []
    for case in load_cases("all"):
        old = case["dir"] / "历史初稿.md"
        if not old.exists():
            continue
        first, second = order_for(case["id"], "历史初稿", "发布版", 0)
        paths = {"历史初稿": old, "发布版": case["dir"] / "定稿.md"}
        packets.append(judge_packet(case, paths[first], paths[second], (first, second), 0, False))
    out = EVAL / "校准.json"
    out.write_text(json.dumps(packets, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(packets)} 个校准任务：{out}")


def text_units(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)", "", text)
    return "".join(ch for ch in text if ch.isalnum())


def overlap(source: str, target: str, k: int = 8) -> float:
    """target 里有多少字落在 source 的连续 k 字片段里。"""
    grams = {source[i:i + k] for i in range(len(source) - k + 1)}
    hit = [False] * len(target)
    for i in range(len(target) - k + 1):
        if target[i:i + k] in grams:
            hit[i:i + k] = [True] * k
    return round(sum(hit) / max(1, len(target)), 3)


def summarize(rows: list[dict], labels: list[str]) -> dict:
    stats = {label: {"赢": 0.0, "场次": 0, "改稿力气": [], "问题": {}, "要点覆盖": []} for label in labels}
    for row in rows:
        mapping = row["order"]
        for side in ("A", "B"):
            label = mapping[side]
            if label not in stats:
                continue
            s = stats[label]
            s["场次"] += 1
            s["赢"] += 1.0 if row["winner"] == side else 0.5 if row["winner"] == "tie" else 0.0
            s["改稿力气"].append(row["effort"][side])
            s["要点覆盖"].append(row["coverage"][side])
            for flag in row["flags"][side]:
                s["问题"][flag] = s["问题"].get(flag, 0) + 1
    result = {}
    for label, s in stats.items():
        n = max(1, s["场次"])
        result[label] = {
            "胜率": round(s["赢"] / n, 3),
            "场次": s["场次"],
            "平均改稿力气": round(sum(s["改稿力气"]) / n, 2),
            "平均要点覆盖": round(sum(s["要点覆盖"]) / n, 3),
            "问题次数": dict(sorted(s["问题"].items(), key=lambda kv: -kv[1])),
        }
    return result


def cmd_score(args: argparse.Namespace) -> None:
    rows = json.loads(Path(args.verdicts).read_text(encoding="utf-8"))
    labels = sorted({row["order"][side] for row in rows for side in ("A", "B")})
    by_split = {split: summarize([r for r in rows if r["split"] == split], labels) for split in ("dev", "holdout")}
    record = {"时间": args.stamp, "文件": args.verdicts, "版本": labels, "开发集": by_split["dev"], "留出集": by_split["holdout"]}

    if set(labels) == {"历史初稿", "发布版"}:
        n = len(rows)
        right = sum(1 for r in rows if r["order"].get(r["winner"]) == "发布版")
        record["评委校准"] = f"{right}/{n} 次选中 Stephen 发布版"
    elif args.new:
        old = next(label for label in labels if label != args.new)
        record["结论"] = gate(by_split, old, args.new)
        record["文字指标"] = text_metrics(labels)

    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False, indent=1))


def gate(by_split: dict, old: str, new: str) -> str:
    dev_new, dev_old = by_split["dev"][new], by_split["dev"][old]
    reasons = []
    if dev_new["胜率"] < 0.5:
        reasons.append(f"开发集胜率 {dev_new['胜率']} 低于 0.5")
    if dev_new["问题次数"].get("编造", 0) > dev_old["问题次数"].get("编造", 0):
        reasons.append("编造次数比旧版多")
    hold = by_split["holdout"].get(new, {})
    if hold.get("场次") and hold["胜率"] < 0.45:
        reasons.append(f"留出集胜率 {hold['胜率']} 低于 0.45，可能只是记住了开发集")
    return "可以上线" if not reasons else "不能上线：" + "；".join(reasons)


def text_metrics(labels: list[str]) -> dict:
    """不靠评委的辅助数字：初稿里有多少被 Stephen 删掉、发布版里有多少初稿已经写到。"""
    out: dict = {}
    for label in labels:
        cut, keep = [], []
        for case in load_cases("all"):
            draft = RUNS / label / case["id"] / "初稿.md"
            if not draft.exists():
                continue
            d, f = text_units(draft), text_units(case["dir"] / "定稿.md")
            cut.append(1 - overlap(f, d))
            keep.append(overlap(d, f))
        if cut:
            out[label] = {"初稿会被删的比例": round(sum(cut) / len(cut), 3), "发布版已被初稿写到的比例": round(sum(keep) / len(keep), 3)}
    return out


def cmd_history(_: argparse.Namespace) -> None:
    if not HISTORY.exists():
        print("还没有评测记录")
        return
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        print(row["时间"], row["版本"], row.get("结论") or row.get("评委校准", ""))
        for split in ("开发集", "留出集"):
            for label, s in row[split].items():
                if s["场次"]:
                    print(f"  {split} {label}: 胜率 {s['胜率']}，改稿力气 {s['平均改稿力气']}，要点覆盖 {s['平均要点覆盖']}")


def cmd_restore(args: argparse.Namespace) -> None:
    tags = git("tag", "--list", "writing-v*").split()
    if args.tag not in tags:
        raise SystemExit(f"没有这个标签。已通过评测的版本：{' '.join(tags) or '无'}")
    if git("status", "--porcelain", "--", SKILL.name):
        raise SystemExit("Skill 目录有未提交的修改，先提交或另存，再恢复")
    git("checkout", args.tag, "--", SKILL.name)
    print(f"已把 {SKILL.name} 恢复成 {args.tag}。确认没问题后按 AGENTS.md 提交并同步；不想要就运行 git checkout HEAD -- {SKILL.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("label")
    p.add_argument("--ref")
    p.add_argument("--split", default="all", choices=["dev", "holdout", "all"])
    p.add_argument("--reuse-drafts", help="复用这个版本那一轮的未审初稿，只重跑审稿和修改")
    p.set_defaults(func=cmd_prepare)
    p = sub.add_parser("pairs")
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--split", default="all", choices=["dev", "holdout", "all"])
    p.set_defaults(func=cmd_pairs)
    sub.add_parser("calibrate").set_defaults(func=cmd_calibrate)
    p = sub.add_parser("score")
    p.add_argument("verdicts")
    p.add_argument("--new", help="新版本名；给了就判断能不能上线")
    p.add_argument("--stamp", default="", help="记录时间")
    p.set_defaults(func=cmd_score)
    sub.add_parser("history").set_defaults(func=cmd_history)
    p = sub.add_parser("restore")
    p.add_argument("tag")
    p.set_defaults(func=cmd_restore)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
