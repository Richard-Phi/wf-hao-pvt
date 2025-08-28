import os

# 输入输出文件
SCHEMAS_DIR = os.getenv('SCHEMAS_DIR', '../schemas/hao')
ASSETS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fullcode_path = os.path.join(SCHEMAS_DIR, 'fullcode_sy_modified.txt')
fullinfo_path = os.path.join(SCHEMAS_DIR, 'hao/hao.sy.fullinformation.dict.yaml')
short_path = os.path.join(SCHEMAS_DIR, 'short_sy.txt')
quicks_path = os.path.join(SCHEMAS_DIR, 'quicks_sy.txt')
output_path = os.path.join(ASSETS_DIR, 'simpcode/res_sy.txt')

# 不生成简码的字
EXCLUDE_CHARS = set('的是不了在我')

# 读取已有的简码字和简码词，建立排除集合
def read_existing_codes(short_path, quicks_path):
    exclude_chars = set()
    exclude_codes = set()
    
    # 读取short_sy.txt
    if os.path.exists(short_path):
        with open(short_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '\t' not in line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    char = parts[0]
                    code = parts[1]
                    exclude_chars.add(char)
                    exclude_codes.add(code)
    
    # 读取quicks_sy.txt
    if os.path.exists(quicks_path):
        with open(quicks_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '\t' not in line:
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    char = parts[0]
                    code = parts[1]
                    exclude_chars.add(char)
                    exclude_codes.add(code)
    
    return exclude_chars, exclude_codes

# 读取已有的简码
existing_chars, existing_codes = read_existing_codes(short_path, quicks_path)
print(f'读取到已有简码字: {len(existing_chars)}个')
print(f'读取到已有简码编码: {len(existing_codes)}个')

# 读取全码表
fullcodes = []  # [(char, code, freq)]
with open(fullcode_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or '\t' not in line:
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        char = parts[0]
        code = parts[1]
        freq = float(parts[2]) if len(parts) > 2 else 0.0
        fullcodes.append((char, code, freq))

print(f'读取到全码条数: {len(fullcodes)}')

# 读取全息码表，建立汉字->全息码映射
def read_fullinfo(path):
    mapping = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '\t' not in line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            char = parts[0]
            code = parts[1]
            mapping[char] = code
    return mapping

fullinfo_map = read_fullinfo(fullinfo_path)

# 建立全码集合
fullcode_set = set(code for _, code, _ in fullcodes)

# 分根函数：每2码为一根，最后剩下的归为最后一根
def split_roots(code):
    if len(code) < 2:
        return None
    roots = []
    i = 0
    while i + 2 < len(code):
        roots.append(code[i:i+2])
        i += 2
    roots.append(code[i:])  # 剩下的归为最后一根
    return roots if len(roots) >= 2 else None

# 生成候选简码函数：全码前缀 + 全息码末根末码
def generate_candidates(full_code, info_code):
    roots = split_roots(info_code)
    if not roots or len(roots) < 2:
        return [], ''
    # 取末根末码
    last_root = roots[-1]
    last_code = last_root[-1] if last_root else ''
    # 计算全码前缀（去掉最后一位）
    prefix = full_code[:-1] if len(full_code) > 1 else ''
    candidates = []
    # 2码简码：全码前缀1码 + 全息码末根末码
    if len(prefix) >= 1:
        candidates.append(prefix[:1] + last_code)
    # 3码简码：全码前缀2码 + 全息码末根末码
    if len(prefix) >= 2:
        candidates.append(prefix[:2] + last_code)
    # 4码简码：全码前缀3码 + 全息码末根末码
    if len(prefix) >= 3:
        candidates.append(prefix[:3] + last_code)
    return candidates, last_code

# 生成简码
simp_dict = {}  # char -> simpcode
used_simp = set()
filtered_conflict_full = 0
filtered_conflict_simp = 0
filtered_too_short = 0
filtered_no_candidates = 0
filtered_exclude = 0
filtered_lastcode_mismatch = 0
filtered_existing_char = 0
filtered_existing_code = 0

total = 0
for char, code, freq in fullcodes:
    total += 1
    if char in EXCLUDE_CHARS:
        filtered_exclude += 1
        continue
    if char in existing_chars:
        filtered_existing_char += 1
        continue
    info_code = fullinfo_map.get(char)
    if not info_code:
        filtered_no_candidates += 1
        continue
    candidates, last_code = generate_candidates(code, info_code)
    if not candidates:
        filtered_no_candidates += 1
        continue
    # 只有全码的最后一位等于全息码末根末码时才允许出简码
    # 但5码字例外，即使末码不匹配也允许出简码
    if code[-1] != last_code and len(code) != 5:
        filtered_lastcode_mismatch += 1
        continue
    # 按优先级选择不冲突的简码
    selected_simp = None
    for simp in candidates:
        # 不能和全码冲突
        if simp in fullcode_set:
            continue
        # 不能和已有简码冲突
        if simp in used_simp:
            continue
        # 不能和已有简码编码冲突
        if simp in existing_codes:
            filtered_existing_code += 1
            continue
        selected_simp = simp
        break
    if selected_simp:
        simp_dict[char] = selected_simp
        used_simp.add(selected_simp)
    else:
        filtered_conflict_simp += 1

print(f'生成简码条数: {len(simp_dict)}')
print(f"被全码冲突过滤: {filtered_conflict_full}")
print(f"被简码冲突过滤: {filtered_conflict_simp}")
print(f"编码过短过滤: {filtered_too_short}")
print(f"无候选简码过滤: {filtered_no_candidates}")
print(f"排除指定字过滤: {filtered_exclude}")
print(f"全码末码与全息码末根末码不符过滤: {filtered_lastcode_mismatch}")
print(f"已有简码字过滤: {filtered_existing_char}")
print(f"已有简码编码冲突过滤: {filtered_existing_code}")

# 输出简码表
with open(output_path, 'w', encoding='utf-8') as f:
    for char, code, freq in fullcodes:
        simp = simp_dict.get(char, '')
        if simp:
            f.write(f'{char}\t{simp}\t{freq:.0f}\n')

print(f'松烟简码生成完毕，输出到 {output_path}，共{len(simp_dict)}条。') 