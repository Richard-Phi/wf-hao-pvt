#!/bin/sh

# 生成大竹碼表
#
# 环境变量:
#   INPUT_DIR: 输入文件目录
#   OUTPUT_DIR: 输出文件目录
#;q	："
#;t	→
#;y	·
#;o	〖
#;p	〗
#;h	『
#;j	』
#;k	￥
#;x	【
#;c	】
#;n	「
#;m	」
# 检查必要的环境变量
if [ -z "${INPUT_DIR}" ] || [ -z "${OUTPUT_DIR}" ]; then
    echo "错误: 需要设置 INPUT_DIR 和 OUTPUT_DIR 环境变量"
    exit 1
fi

# 生成大竹码表
if [ -f "${INPUT_DIR}/hao/hao.xi.short.dict.yaml" ]; then
    cat "${INPUT_DIR}/hao/hao.xi.short.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $2 "\t" $1}' | \
        sed 's/1/_/g' | \
        sed 's/2/;/g' | \
        sed "s/3/'/g" \
        >"${OUTPUT_DIR}/hao/dazhu-xi.txt"
    
    cat "${INPUT_DIR}/hao/hao.xi.full.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $2 "\t" $1}' | \
        sed 's/1/_/g' | \
        sed 's/2/;/g' | \
        sed "s/3/'/g" \
        >>"${OUTPUT_DIR}/hao/dazhu-xi.txt"

    # 修正快符
    xi_file="${OUTPUT_DIR}/hao/dazhu-xi.txt"
    match_line=$(grep -n '：“' "$xi_file" | head -n1 | cut -d: -f1)
    if [ -n "$match_line" ]; then
      start_line=$match_line
      end_line=$((match_line+20))
      tmp_file="${xi_file}.tmp"
      awk -v s=$start_line -v e=$end_line '{if(NR>=s && NR<=e){print ";"$0} else {print $0}}' "$xi_file" > "$tmp_file" && mv "$tmp_file" "$xi_file"
    fi

    if [ -f "${INPUT_DIR}/div_xi.txt" ]; then
        #cat "${INPUT_DIR}/div_xi.txt" | \
        #    sed 's/\(.*\)\t\(.*\)/\2\t\1/g' \
        #    >>"${OUTPUT_DIR}/hao/dazhu-xi.txt" && \
        cat "${INPUT_DIR}/div_xi.txt" | \
            sed 's/\(.*\)\t(\(.*\),.*\(,.*,.*,.*\))/\2\3\t\1/g' \
            >"${OUTPUT_DIR}/hao/dazhu-haochai.txt"
    fi
fi

if [ -f "${INPUT_DIR}/hao/hao.sy.short.dict.yaml" ]; then
    cat "${INPUT_DIR}/hao/hao.sy.short.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\2\t\1/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        #awk '{print $2"\t"$1}' | \
        sed 's/1/_/g' | \
        sed 's/2/;/g' | \
        sed "s/3/'/g" \
        >>"${OUTPUT_DIR}/hao/dazhu-sy.txt"
    
    cat "${INPUT_DIR}/hao/hao.sy.quicks.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\2\t\1/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        #awk '{print $2"\t"$1}' | \
        sed 's/1/_/g' | \
        sed 's/2/;/g' | \
        sed "s/3/'/g" \
        >>"${OUTPUT_DIR}/hao/dazhu-sy.txt"
    
    cat "${INPUT_DIR}/hao/hao.sy.full.dict.yaml" | \
        sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
        sed 's/\t/{TAB}/g' | \
        grep '.*{TAB}.*' | \
        sed 's/{TAB}/\t/g' | \
        awk '{print $2 "\t" $1}' | \
        sed 's/1/_/g' | \
        sed 's/2/;/g' | \
        sed "s/3/'/g" \
        >>"${OUTPUT_DIR}/hao/dazhu-sy.txt"

    #if [ -f "${INPUT_DIR}/div_sy.txt" ]; then
    #    cat "${INPUT_DIR}/div_sy.txt" | \
    #        sed 's/\(.*\)\t\(.*\)/\2\t\1/g' \
    #        >>"${OUTPUT_DIR}/hao/dazhu-sy.txt"
    #fi
fi

#sed 's/^\(.*\)\t\(.*\)/\1\t\2/g' | \
#    sed 's/\t/{TAB}/g' | \
#    grep '.*{TAB}.*' | \
#    sed -E 's/(\W+){TAB}([0-9a-z]+).*\n/\1{TAB}\2\n/g' #| \
#    #sed 's/1/_/g' | \
#    #sed 's/2/_/g' | \
    #sed "s/3/_/g" #| \
    #sed 's/\(.*\){TAB}\(.*\)/\2\t\1/g'
