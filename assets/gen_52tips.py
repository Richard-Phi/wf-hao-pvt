import argparse
import sys
import itertools
import string

def generate_all_combinations():
    """生成所有4字母组合（a-z）"""
    alphabet = string.ascii_lowercase
    return (''.join(combo) for combo in itertools.product(alphabet, repeat=4))

def load_char_mapping(input_path):
    """加载字符映射关系"""
    char_dict = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) < 2:
                continue
                
            prefix, char = parts[0], parts[1]
            
            # 处理键
            if prefix.endswith(';'):
                key = prefix.rstrip(';')
                char_dict.setdefault(key, ['', ''])[1] = char
            else:
                char_dict.setdefault(prefix, ['', ''])[0] = char
    return char_dict

def generate_output_lines(char_dict):
    """生成所有456,976行输出"""
    results = []
    # 生成所有4字母组合
    for full_key in generate_all_combinations():
        # 拆分4字母键为两个2字母键
        key1 = full_key[:2]
        key2 = full_key[2:]
        
        # 获取字符映射（如果不存在则使用空字符串）
        j1, f1 = char_dict.get(key1, ['', ''])
        j2, f2 = char_dict.get(key2, ['', ''])
        
        # 构建输出行
        line = f"_{j1}{j2} ;{j1}{f2} 4{f1}{j2} 7{f1}{f2}\t{full_key}"
        results.append(line)
    return results

def convert_file(input_path, output_path):
    try:
        # 加载字符映射
        char_dict = load_char_mapping(input_path)
        
        # 生成所有输出行
        results = generate_output_lines(char_dict)
        
        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
            
        print(f"转换成功! 已生成 {len(results):,} 行数据到 {output_path}")
        print(f"组合总数: 26^4 = {26**4:,} (a-z的四位组合)")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='全组合文件生成器')
    parser.add_argument('input', help='字符映射文件路径')
    parser.add_argument('output', help='输出文件路径')
    
    args = parser.parse_args()
    
    convert_file(args.input, args.output)