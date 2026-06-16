"""Markdown 预处理：公式、表格、图片等（专著与章节打包共用）。"""

from __future__ import annotations

import re


CJK_RANGE = r'\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u3400-\u4dbf'
CJK_CONT_RE = re.compile(f'[{CJK_RANGE}，。；：！？、（）【】《》""''…—]+')


def strip_frontmatter(text: str) -> str:
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL, count=1)
    return text.replace('{% raw %}', '').replace('{% endraw %}', '').replace('<!--more-->', '')


def wrap_chinese_in_math(math_body: str) -> str:
    result: list[str] = []
    i = 0
    while i < len(math_body):
        if math_body[i:].startswith(r'\text{') or math_body[i:].startswith(r'\mbox{'):
            brace_start = math_body.index('{', i) + 1
            depth = 1
            j = brace_start
            while j < len(math_body) and depth > 0:
                if math_body[j] == '{':
                    depth += 1
                elif math_body[j] == '}':
                    depth -= 1
                j += 1
            result.append(math_body[i:j])
            i = j
            continue

        if math_body[i] == '\\':
            j = i + 1
            if j < len(math_body) and math_body[j] in r'{}$%&_^~# ':
                result.append(math_body[i : j + 1])
                i = j + 1
                continue
            while j < len(math_body) and math_body[j].isalpha():
                j += 1
            if j < len(math_body) and math_body[j] == '{':
                depth = 1
                j += 1
                while j < len(math_body) and depth > 0:
                    if math_body[j] == '{':
                        depth += 1
                    elif math_body[j] == '}':
                        depth -= 1
                    j += 1
            result.append(math_body[i:j])
            i = j
            continue

        m = CJK_CONT_RE.match(math_body, i)
        if m:
            result.append(r'\text{' + m.group(0) + '}')
            i = m.end()
            continue

        result.append(math_body[i])
        i += 1

    return ''.join(result)


def preprocess_math(text: str) -> str:
    def fix_display_math(m: re.Match[str]) -> str:
        body = wrap_chinese_in_math(m.group(1))
        return r'\[' + body + r'\]'

    text = re.sub(r'\\\[(.+?)\\\]', fix_display_math, text, flags=re.DOTALL)

    def fix_display_dollar(m: re.Match[str]) -> str:
        body = re.sub(r'\n\s*\n', '\n', m.group(1))
        body = wrap_chinese_in_math(body)
        return '$$' + body + '$$'

    text = re.sub(r'\$\$(.+?)\$\$', fix_display_dollar, text, flags=re.DOTALL)

    def fix_inline_math(m: re.Match[str]) -> str:
        body = m.group(1)
        if r'\begin{cases}' in body or '\\begin{cases}' in body:
            body = wrap_chinese_in_math(body)
            return '\n$$' + body + '$$\n'
        body = wrap_chinese_in_math(body)
        return '$' + body + '$'

    text = re.sub(r'(?<!\$)\$(?!\$)((?:[^$]|\\\$)+?)\$(?!\$)', fix_inline_math, text)
    return text


def _render_table_as_text(lines: list[str]) -> str:
    data_lines = [l for l in lines if not re.match(r'^\|[\s\-:|]+\|$', l.strip())]
    if not data_lines:
        return ''
    text_lines = ['', '```text']
    for dl in data_lines:
        cells = [c.strip() for c in dl.strip().strip('|').split('|')]
        text_lines.append('  ' + ' | '.join(cells))
    text_lines.append('```')
    text_lines.append('')
    return '\n'.join(text_lines)


def markdown_table_to_text(content: str) -> str:
    lines = content.split('\n')
    result: list[str] = []
    in_table = False
    table_lines: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_table_line = bool(re.match(r'^\|.*\|$', stripped))
        is_separator = bool(re.match(r'^\|[\s\-:|]+\|$', stripped))
        prev_is_table = i > 0 and bool(re.match(r'^\|.*\|$', lines[i - 1].strip()))

        if is_table_line or (is_separator and prev_is_table):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        else:
            if in_table:
                result.append(_render_table_as_text(table_lines))
                table_lines = []
                in_table = False
            result.append(line)

    if in_table and table_lines:
        result.append(_render_table_as_text(table_lines))

    return '\n'.join(result)


def preprocess_content(content: str, url_map: dict[str, str | None] | None = None) -> str:
    """综合预处理：图片、HTML、表格、公式等。"""
    if url_map is not None:

        def _replace_img(m: re.Match[str]) -> str:
            alt = m.group(1) or ''
            url = m.group(2)
            local = url_map.get(url)
            return f'![{alt}]({local})' if local else f'[图: {alt}]'

        content = re.sub(r'!\[([^\]]*)\]\((https?://[^)]+)\)', _replace_img, content)
    else:
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[图: \1]', content)

    content = re.sub(r'<details[^>]*>.*?</details>', '', content, flags=re.DOTALL)
    content = re.sub(r'<summary[^>]*>.*?</summary>', '', content, flags=re.DOTALL)
    content = re.sub(r'</?br\s*/?>', r'\\', content)
    content = markdown_table_to_text(content)
    content = content.replace('------', '——').replace('-----', '——')
    content = re.sub(r'\\sub(?![a-zA-Z])', r'\\subset', content)
    content = re.sub(r'\\\(\$([^$]+?)\$\\\)', r'\\(\1\\)', content)
    content = re.sub(r'\$\\\(([^)]+?)\\\)\$', r'\\(\1\\)', content)

    # 将 \\| 范数替换为 \\lVert / \\rVert（避免 Liquid 管道符截断）
    def _replace_norm_pipes(text: str) -> str:
        result: list[str] = []
        i = 0
        expect_open = True
        while i < len(text):
            if text[i:i+2] == '\\|':
                if expect_open:
                    result.append('\\lVert ')
                    expect_open = False
                else:
                    result.append('\\rVert ')
                    expect_open = True
                i += 2
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
    content = _replace_norm_pipes(content)

    def _strip_inner(m: re.Match[str]) -> str:
        return '$' + m.group(1).strip() + '$'

    for _ in range(3):
        content = re.sub(r'(?<!\$)\$ ([^$]+?)\$(?!\$)', _strip_inner, content)
        content = re.sub(r'(?<!\$)\$([^$]+?) \$(?!\$)', _strip_inner, content)

    content = preprocess_math(content)

    def _wrap(m: re.Match[str]) -> str:
        return ' $' + m.group(1) + '$ '

    content = re.sub(r'(?<!\$)\$([^\n$]+?)\$(?!\$)', _wrap, content)
    return content
