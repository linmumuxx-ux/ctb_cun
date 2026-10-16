# -*- coding: utf-8 -*-
"""按题面二级章节切分子系统。

规则与 e2e-test/SKILL.md「切分」一节一致，供编排器和 validation/selftest.py 共用。
只读题目里的 Markdown，不写测试规格。
"""
from __future__ import print_function

import json
import os
import re
import sys

# 这些标题是文档结构，不是业务子系统。
GENERIC = set([
    "命令", "规则", "概述", "说明", "成功", "失败", "约束", "范围",
    "错误码", "接口说明", "输入", "输出", "示例", "附录", "背景", "目标",
])

H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
SKIP_DIRS = set([".ctb", ".git", "python_framework", "__pycache__"])


def _norm(title):
    return re.sub(r"[（(].*?[）)]", "", title.strip()).strip()


def segment_text(text, fallback="主体"):
    """返回子系统列表。少于两个有效二级标题时退化为单模块。"""
    heads = []
    for match in H2.finditer(text or ""):
        raw = match.group(1).strip()
        if _norm(raw) in GENERIC:
            continue
        heads.append(raw)
    if len(heads) >= 2:
        return [{"id": "S%02d" % i, "name": name, "single": False}
                for i, name in enumerate(heads, 1)]
    found = H1.search(text or "")
    name = found.group(1).strip() if found else fallback
    return [{"id": "S01", "name": name, "single": True}]


def read_subject_markdown(subject_root):
    chunks = []
    for base, dirs, files in os.walk(subject_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(base, name)
            with open(path, "r", encoding="utf-8") as handle:
                chunks.append(handle.read())
    return "\n".join(chunks)


def segment_subject(subject_root):
    root = os.path.abspath(subject_root)
    text = read_subject_markdown(root)
    return segment_text(text, fallback=os.path.basename(root))


def main(argv):
    if len(argv) != 2:
        print("usage: segment_subject.py <subject_root>", file=sys.stderr)
        return 2
    json.dump(segment_subject(argv[1]), sys.stdout, ensure_ascii=False, indent=2)
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
