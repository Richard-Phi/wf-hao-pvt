#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用的单字码表去重工具
删除重复的「编码\t汉字」行，只有当编码和汉字都相同时才视为重复
"""

import os
import sys
import argparse

def remove_duplicate_chars(input_file, output_file=None):
    """
    删除重复的「编码\t汉字」行，只有当编码和汉字都相同时才视为重复
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径，如果为None则自动生成
    
    Returns:
        tuple: (原始行数, 去重后行数, 删除的重复行数)
    """
    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        return None
    
    # 如果未指定输出文件，自动生成
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_去重.txt"
    
    seen_items = set()    # 用于记录已经出现过的(编码,汉字)组合
    unique_lines = []     # 存储去重后的行
    duplicate_count = 0   # 重复行计数
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                # 分割编码和汉字
                parts = line.split('\t')
                if len(parts) != 2:
                    print(f"警告：第{line_num}行格式不正确，跳过: {line}")
                    continue
                
                code, char = parts
                item = (code, char)  # 使用元组存储编码和汉字组合
                
                # 如果这个(编码,汉字)组合还没有出现过，则保留
                if item not in seen_items:
                    seen_items.add(item)
                    unique_lines.append(line)
                else:
                    duplicate_count += 1
                    # 注释掉下面的print语句以去除删除重复行的提示
                    # print(f"删除重复行 '{code}\t{char}' (第{line_num}行)")
        
        # 写入去重后的内容
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in unique_lines:
                f.write(line + '\n')
        
        original_count = len(unique_lines) + duplicate_count
        
        print(f"\n去重完成！")
        print(f"原始文件行数: {original_count}")
        print(f"去重后行数: {len(unique_lines)}")
        print(f"删除的重复行数: {duplicate_count}")
        print(f"结果已保存到: {output_file}")
        
        return original_count, len(unique_lines), duplicate_count
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='删除单字码表中重复的「编码\t汉字」行，只有当编码和汉字都相同时才视为重复')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，默认自动生成）')
    
    args = parser.parse_args()
    
    print("开始删除重复行...")
    print(f"输入文件: {args.input_file}")
    if args.output:
        print(f"输出文件: {args.output}")
    else:
        print("输出文件: 自动生成")
    print("-" * 50)
    
    result = remove_duplicate_chars(args.input_file, args.output)
    
    if result:
        original_count, unique_count, duplicate_count = result
        print(f"\n统计信息:")
        print(f"  - 原始行数: {original_count}")
        print(f"  - 去重后行数: {unique_count}")
        print(f"  - 删除重复行数: {duplicate_count}")
        print(f"  - 重复率: {duplicate_count/original_count*100:.2f}%")

if __name__ == "__main__":
    # 如果没有命令行参数，使用默认文件
    if len(sys.argv) == 1:
        input_file = "data/单字码表_haosy.txt"
        output_file = "data/单字码表_haosy_去重.txt"
        
        print("使用默认文件:")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print("-" * 50)
        
        remove_duplicate_chars(input_file, output_file)
    else:
        main()