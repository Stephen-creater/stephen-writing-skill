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

DISALLOWED_PATTERNS = (
    (re.compile(r'不是[^。！？\n]{0,24}而是'), '翻案句「不是 X，而是 Y」'),
    (re.compile(r'并非[^。！？\n]{0,24}而是'), '翻案句「并非 X，而是 Y」'),
    (re.compile(r'不在于[^。！？\n]{0,24}而在于'), '翻案句「不在于 X，而在于 Y」'),
    (re.compile(r'与其说[^。！？\n]{0,24}不如说'), '翻案句「与其说 X，不如说 Y」'),
    (re.compile(r'是[^。！？\n]{1,20}[，,]\s*不是'), '翻案句「是 X，不是 Y」'),
)


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
        for pattern, label in DISALLOWED_PATTERNS:
            for match in pattern.finditer(line):
                issues.append(
                    Issue(
                        line=line_number,
                        column=match.start() + 1,
                        character=match.group(),
                        label=label,
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
