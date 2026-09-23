#!/usr/bin/env python3
"""Deterministically assemble the standalone prompt from the skill sources."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'hcds-expression-refactor'
OUTPUT = ROOT / 'dist' / 'hcds-expression-refactor.prompt.md'


def render():
    source = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    if not source.startswith('---\n') or '\n---\n' not in source[4:]:
        raise ValueError('SKILL.md must begin with YAML frontmatter')
    body = source.split('\n---\n', 1)[1].strip()
    references = []

    def inline_reference(match):
        label, relative = match.groups()
        path = (SKILL / relative).resolve()
        if not path.is_relative_to((SKILL / 'references').resolve()):
            raise ValueError(f'Reference outside references directory: {relative}')
        if path not in references:
            references.append(path)
        return f'下文内嵌的「{label}」'

    body = re.sub(r'\[([^\]]+)\]\((references/[^)]+\.md)\)', inline_reference, body)
    sections = [body]
    for path in references:
        # Nest reference headings under the main prompt, preserving all rules.
        content = path.read_text(encoding='utf-8').strip()
        sections.append(re.sub(r'^(#{1,5}) ', r'\1# ', content, flags=re.MULTILINE))
    result = '\n\n'.join(sections) + '\n'
    if 'references/' in result:
        raise ValueError('Unexpanded references/ dependency in prompt')
    return result.encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without writing files')
    args = parser.parse_args()
    try:
        expected = render()
    except (OSError, ValueError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1
    if args.check:
        if not OUTPUT.exists():
            print(f'Missing: {OUTPUT}', file=sys.stderr)
            return 1
        if OUTPUT.read_bytes() != expected:
            print(f'Out of date: {OUTPUT}', file=sys.stderr)
            return 1
        print(f'Up to date: {OUTPUT}')
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(expected)
    print(f'Generated: {OUTPUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
