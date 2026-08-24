from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DISALLOWED = {
    '“': '中文左双引号',
    '”': '中文右双引号',
    '"': '英文双引号',
    '—': '破折号',
    '–': '连接号式破折号',
}


@dataclass(frozen=True)
class Issue:
    line: int
    column: int
    character: str
    label: str


def prose_lines(text: str):
    in_fence = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        without_inline_code = re.sub(r'`[^`]*`', '', line)
        yield line_number, without_inline_code


def find_issues(text: str) -> list[Issue]:
    issues: list[Issue] = []
    for line_number, line in prose_lines(text):
        for column, character in enumerate(line, start=1):
            if character in DISALLOWED:
                issues.append(
                    Issue(
                        line=line_number,
                        column=column,
                        character=character,
                        label=DISALLOWED[character],
                    )
                )
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description='检查正文中的引号和破折号')
    parser.add_argument('path', type=Path)
    args = parser.parse_args()

    text = args.path.read_text(encoding='utf-8')
    issues = find_issues(text)
    if not issues:
        print('标点检查通过')
        return

    for issue in issues:
        print(
            f'{args.path}:{issue.line}:{issue.column}: '
            f'{issue.label} {issue.character}'
        )
    raise SystemExit(1)


if __name__ == '__main__':
    main()
