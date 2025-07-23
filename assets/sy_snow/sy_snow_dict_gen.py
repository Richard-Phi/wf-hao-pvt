import os
import argparse

def load_single_code_dict(path):
    code_dict = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("---"):
                continue
            # 跳过yaml头部
            if line.startswith("name:") or line.startswith("version:") or line.startswith("sort:") or line.startswith("columns:") or line.startswith("- "):
                continue
            if line.startswith("..."):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            char = parts[0].strip()
            code = parts[1].strip()
            code_dict[char] = code
    return code_dict

def process_multi_word_file(input_path, output_path, code_dict):
    with open(input_path, encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            # 支持多字词和词频两列，tab或空格分隔
            if "\t" in line:
                word, freq = line.split("\t", 1)
            elif " " in line:
                word, freq = line.split(" ", 1)
            else:
                word, freq = line, ""
            word = word.strip()
            freq = freq.strip()
            if len(word) < 2:
                continue
            codes = []
            for char in word:
                code = code_dict.get(char, "")
                codes.append(code)
            if all(codes):
                if freq:
                    fout.write(f"{word}\t{' '.join(codes)}\t{freq}\n")
                else:
                    fout.write(f"{word}\t{' '.join(codes)}\n")

def parse_args():
    parser = argparse.ArgumentParser(description="多字词全息码表生成器")
    parser.add_argument("--single-code", required=True, help="单字全息码表路径")
    parser.add_argument("--inout", action="append", required=True, help="多字词输入输出文件对，格式为in.txt:out.txt，可多次传递")
    return parser.parse_args()

def main():
    args = parse_args()
    single_code_path = args.single_code
    inout_pairs = {}
    for pair in args.inout:
        if ":" not in pair:
            print(f"参数格式错误: {pair}，应为in.txt:out.txt")
            continue
        in_path, out_path = pair.split(":", 1)
        inout_pairs[in_path] = out_path

    code_dict = load_single_code_dict(single_code_path)
    for in_path, out_path in inout_pairs.items():
        process_multi_word_file(in_path, out_path, code_dict)
    print("多字词全息码表已生成。")

if __name__ == "__main__":
    main()