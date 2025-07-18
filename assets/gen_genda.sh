#!/bin/sh

# 生成跟打词提
#
# 环境变量:
#   INPUT_DIR: 输入文件目录
#   OUTPUT_DIR: 输出文件目录

# 检查必要的环境变量
if [ -z "${INPUT_DIR}" ] || [ -z "${OUTPUT_DIR}" ]; then
    echo "错误: 需要设置 INPUT_DIR 和 OUTPUT_DIR 环境变量"
    exit 1
fi

# 生成跟打词提
if [ -f "${INPUT_DIR}/hao/hao.xi.short.dict.yaml" ]; then
    cat "${INPUT_DIR}/hao/hao.xi.short.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $1 "\t" $2}' \
        >"${OUTPUT_DIR}/hao/跟打词提-淅码.txt"
    
    cat "${INPUT_DIR}/hao/hao.xi.full.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $1 "\t" $2}' \
        >>"${OUTPUT_DIR}/hao/跟打词提-淅码.txt"
fi

if [ -f "${INPUT_DIR}/hao/hao.sy.short.dict.yaml" ]; then
    cat "${INPUT_DIR}/hao/hao.sy.short.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' \
        >>"${OUTPUT_DIR}/hao/跟打词提-松烟.txt"
    
    cat "${INPUT_DIR}/hao/hao.sy.quicks.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\2\t\1/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $2 "\t" $1}' \
        >>"${OUTPUT_DIR}/hao/跟打词提-松烟.txt"
    
    cat "${INPUT_DIR}/hao/hao.sy.full.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $1 "\t" $2}' \
        >>"${OUTPUT_DIR}/hao/跟打词提-松烟.txt"
fi
