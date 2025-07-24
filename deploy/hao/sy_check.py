# coding: utf-8

import argparse

parser = argparse.ArgumentParser(description="检查txt文件中是否有重复编码（第二列）")
parser.add_argument("file_paths", nargs="+", help="要检查的txt文件路径（可多个）")
args = parser.parse_args()

for file_path in args.file_paths:
    code_map = {}
    duplicates = []
    print(f"\n正在检查文件：{file_path}")
    try:
        with open(file_path, encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                word, code = parts[0], parts[1]
                if code in code_map:
                    duplicates.append((idx, word, code, code_map[code]))
                else:
                    code_map[code] = (idx, word)
        if duplicates:
            print("发现重复编码：")
            for idx, word, code, (prev_idx, prev_word) in duplicates:
                print(f"第{idx}行【{word}】与第{prev_idx}行【{prev_word}】编码重复：{code}")
        else:
            print("未发现重复编码。")
    except Exception as e:
        print(f"文件读取失败：{e}")