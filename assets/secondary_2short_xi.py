# 生成所有两位编码（aa到zz）
prefixes = [a + b for a in 'abcdefghijklmnopqrstuvwxyz' for b in 'abcdefghijklmnopqrstuvwxyz']

# 读取码表文件，构建字典：键为两位前缀，值为该前缀下的所有条目（按文件出现顺序）
prefix_map = {p: [] for p in prefixes}

# 存储二简二重结果
secondary_results = {}

with open('../schemas/hao/hao/dazhu-xi52.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        code = parts[0].lower()  # 统一转为小写
        char = parts[1]
        # 只处理长度>=2的编码
        if len(code) >= 2:
            p = code[:2]
            if p in prefix_map:
                # 直接按文件顺序添加条目
                prefix_map[p].append((code, char))

# 1. 输出二简二重码表文件
with open('../schemas/hao/淅码五二顶二简二重表.txt', 'w', encoding='utf-8') as out_f:
    for p in prefixes:
        entries = prefix_map[p]
        if len(entries) >= 2:
            # 取该前缀下按文件顺序出现的第二个条目
            second_code, second_char = entries[1]
            secondary_results[p] = second_char
            out_f.write(f"{p};\t{second_char}\n")
        else:
            out_f.write(f"{p};\t\n")

# 2. 更新原始码表：在第一次出现的汉字前插入二简二重码行
# 记录哪些汉字已经被插入过
inserted_chars = set()

# 存储更新后的码表行
updated_lines = []

# 第一次遍历：在第一次出现的汉字前插入新行
with open('../schemas/hao/hao/dazhu-xi52.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            updated_lines.append(line)
            continue

        parts = line.split('\t')
        if len(parts) < 2:
            updated_lines.append(line)
            continue

        char = parts[1]

        # 如果该汉字是二简二重字且尚未插入过
        if char in secondary_results.values() and char not in inserted_chars:
            # 找到对应的两位编码
            for p, c in secondary_results.items():
                if c == char:
                    # 在该行之前插入新行
                    updated_lines.append(f"{p};\t{c}")
                    inserted_chars.add(char)
                    break

        # 原行保留
        updated_lines.append(line)

# 第二次遍历：添加未插入的二简二重字（如果原始码表中没有出现过）
for p, char in secondary_results.items():
    if char not in inserted_chars:
        updated_lines.append(f"{p};\t{char}")
        inserted_chars.add(char)

# 3. 输出修正后的码表
with open('../schemas/hao/hao/dazhu-xi52-fix.txt', 'w', encoding='utf-8') as out_f:
    for line in updated_lines:
        out_f.write(line + '\n')

print("处理完成！")
print(f"1. 二简二重码表已输出到: secondary_2short_xi.txt")
print(f"2. 修正后的码表已输出到: dazhu-xi52-fix.txt")