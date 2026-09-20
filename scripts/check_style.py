"""数出正文的字数，以及容易带 AI 味的标点和句式：双引号、破折号、先否定再肯定的句式。

这些东西大多数时候不用，但写得自然的文章偶尔出现一两处没关系，所以脚本只在数量偏多时
返回失败，数量少时列出来供审稿人判断。代码块和行内代码不算。

用法：python3 check_style.py 文章.md
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

QUOTES = {'“': '中文双引号', '”': '中文双引号', '"': '英文双引号'}
DASHES = {'—': '破折号', '–': '破折号'}
TURNS = (
    re.compile(r'不是[^。！？\n]{0,24}而是'),
    re.compile(r'并非[^。！？\n]{0,24}而是'),
    re.compile(r'不在于[^。！？\n]{0,24}而在于'),
    re.compile(r'与其说[^。！？\n]{0,24}不如说'),
    re.compile(r'是[^。！？\n]{1,20}[，,]\s*不是(?!吗)'),
)
# 超过这些数量就算偏多：双引号按对数，破折号按处数，句式按句数。
LIMITS = {'双引号': 3, '破折号': 2, '先否定再肯定': 2}


@dataclass(frozen=True)
class Issue:
    line: int
    kind: str
    text: str


def prose_lines(text: str):
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, re.sub(r'`[^`]*`', '', line)


def find_issues(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for number, line in prose_lines(text):
        linked_dash = {i for m in re.finditer(r'——(?=\[)', line) for i in range(m.start(), m.end())}
        for column, char in enumerate(line):
            if char in QUOTES:
                issues.append(Issue(number, '双引号', char))
            elif char in DASHES and column not in linked_dash:
                issues.append(Issue(number, '破折号', char))
        for pattern in TURNS:
            for match in pattern.finditer(line):
                issues.append(Issue(number, '先否定再肯定', match.group()))
    return issues


def counts(issues: list[Issue]) -> dict[str, int]:
    quote_chars = sum(1 for i in issues if i.kind == '双引号')
    dash_lines = {i.line for i in issues if i.kind == '破折号'}
    return {
        '双引号': (quote_chars + 1) // 2,
        '破折号': len(dash_lines),
        '先否定再肯定': sum(1 for i in issues if i.kind == '先否定再肯定'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='数出双引号、破折号和先否定再肯定的句式')
    parser.add_argument('path', type=Path)
    args = parser.parse_args()

    text = args.path.read_text(encoding='utf-8')
    body = re.sub(r'```.*?```', '', text, flags=re.S)
    chinese = len(re.findall(r'[\u4e00-\u9fff]', body))
    print(f'字数：汉字 {chinese}，去空白共 {len(re.sub(r"[ \t\n]", "", body))}（不含代码块）')
    issues = find_issues(text)
    total = counts(issues)
    for issue in issues:
        print(f'{args.path}:{issue.line}: {issue.kind} {issue.text}')
    over = {kind: n for kind, n in total.items() if n > LIMITS[kind]}
    summary = '，'.join(f'{kind} {n}' for kind, n in total.items())
    if over:
        print(f'偏多，需要改：{summary}（上限：双引号 3 对、破折号 2 处、先否定再肯定 2 句）')
        raise SystemExit(1)
    print(f'数量不多：{summary}。读着自然可以不改。' if issues else '没有发现')


if __name__ == '__main__':
    main()
