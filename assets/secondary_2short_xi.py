#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# ==================== 配置 ====================
# 设为 True → 在对应汉字的**前一行**插入二简二重码
# 设为 False → 直接**替换**第一次出现的完整码
INSERT_BEFORE = True

# 输入/输出路径（相对或绝对均可）
SRC_FILE   = Path("../schemas/hao/hao/dazhu-xi52.txt")
OUT_FIX    = Path("../schemas/hao/hao/dazhu-xi52-fix.txt")
OUT_TABLE  = Path("../schemas/hao/淅码五二顶二简二重表.txt")
# =============================================

# ---------- 1. 生成所有两位前缀 ----------
prefixes = [a + b for a in "abcdefghijklmnopqrstuvwxyz" for b in "abcdefghijklmnopqrstuvwxyz"]
prefix_map = {p: [] for p in prefixes}
secondary_results = {}   # {prefix: char}

# ---------- 2. 读取原始码表，收集二简二重 ----------
with SRC_FILE.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code, char = parts[0].lower(), parts[1]
        if len(code) >= 2:
            p = code[:2]
            if p in prefix_map:
                prefix_map[p].append((code, char))

# ---------- 3. 写二简二重表 ----------
with OUT_TABLE.open("w", encoding="utf-8") as out_f:
    for p in prefixes:
        entries = prefix_map[p]
        if len(entries) >= 2:
            # 取第二个出现的条目
            second_code, second_char = entries[1]
            secondary_results[p] = second_char
            out_f.write(f"{p};\t{second_char}\n")
        else:
            out_f.write(f"{p};\t\n")

# ---------- 4. 修正原始码表 ----------
# 已经写入二简二重的汉字集合（防止同一个字被多次插入/替换）
handled_chars = set()
# 最终行列表
fixed_lines = []

with SRC_FILE.open("r", encoding="utf-8") as f:
    for raw_line in f:
        line = raw_line.rstrip("\n")          # 保留可能的前后空格，后面统一处理
        stripped = line.strip()
        if not stripped:
            fixed_lines.append(line)
            continue

        parts = stripped.split("\t")
        if len(parts) < 2:
            fixed_lines.append(line)
            continue

        code, char = parts[0], parts[1]

        # 判断此字符是否是二简二重字且尚未处理
        if char in secondary_results.values() and char not in handled_chars:
            # 找到对应的两位前缀
            for p, c in secondary_results.items():
                if c == char:
                    new_entry = f"{p};\t{char}"
                    if INSERT_BEFORE:
                        # 先写二简二重，再写原始行（保持原始行不变）
                        fixed_lines.append(new_entry)
                        fixed_lines.append(line)   # 保留原始行
                    else:
                        # 直接用二简二重码覆盖原始行
                        fixed_lines.append(new_entry)
                    handled_chars.add(char)
                    break
        else:
            fixed_lines.append(line)

# ---------- 5. 处理“原码表里没有出现”的二简二重字 ----------
for p, char in secondary_results.items():
    if char not in handled_chars:
        new_entry = f"{p};\t{char}"
        if INSERT_BEFORE:
            # 直接追加到文件末尾（因为找不到对应的“前一行”）
            fixed_lines.append(new_entry)
        else:
            fixed_lines.append(new_entry)
        handled_chars.add(char)

# ---------- 6. 写回修正后的码表 ----------
with OUT_FIX.open("w", encoding="utf-8") as out_f:
    for l in fixed_lines:
        out_f.write(l + "\n")

# ---------- 7. 完成提示 ----------
print("处理完成！")
print(f"二简二重表已写入: {OUT_TABLE}")
print(f"修正后的码表已写入: {OUT_FIX}")
print(f"当前模式：{'在前一行插入' if INSERT_BEFORE else '直接替换'}")
