#!/bin/bash

# 好码输入法部署脚本
# 用途：生成好码输入法的 RIME 方案并打包发布
# 作者：荒
# 最后更新：$(date +%Y-%m-%d)

set -e  # 遇到错误立即退出
set -u  # 使用未定义的变量时报错

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

error() {
    log "错误: $1" >&2
    exit 1
}

# 检测操作系统类型
OS_TYPE=$(uname)

# 初始化环境变量和工作目录
#source ~/.zshrc

cd "$(dirname $0)" || error "无法切换到脚本目录"
WD="$(pwd)"
SCHEMAS="../schemas"
REF_NAME="${REF_NAME:-v$(date +%Y%m%d%H%M)}"

# 创建内存中的临时目录
create_ramdisk() {
    local size="512M"
    
    if [ "${OS_TYPE}" = "Darwin" ]; then
        # macOS 实现
        RAMDISK=$(mktemp -d) || error "无法创建临时目录"
        # macOS 下使用原生临时文件系统，它默认就在内存中
        trap 'log "清理临时文件..."; rm -rf "${RAMDISK}"' EXIT
    elif [ "${OS_TYPE}" = "Linux" ]; then
        # Linux 实现 - 修改为不使用 mount 命令
        RAMDISK=$(mktemp -d) || error "无法创建临时目录"
        # 在 GitHub Actions 中，直接使用 /tmp 目录，不需要额外挂载
        trap 'log "清理临时文件..."; rm -rf "${RAMDISK}"' EXIT
    else
        error "不支持的操作系统: ${OS_TYPE}"
    fi
    
    log "成功创建内存临时目录: ${RAMDISK}"
}

# 清理和准备目录
rm -rf "${SCHEMAS}/hao/build" "${SCHEMAS}/releases"
create_ramdisk
mkdir -p "${SCHEMAS}/releases"

# 生成输入方案
gen_schema() {
    local NAME="$1"
    local DESC="${2:-${NAME}}"
    
    if [ -z "${NAME}" ]; then
        error "方案名称不能为空"
    fi
    
    log "开始生成方案: ${NAME}"
    
    local HAO="${RAMDISK}/${NAME}"
    # 设置环境变量
    export SCHEMAS_DIR="${HAO}"
    export ASSETS_DIR="${HAO}"
    mkdir -p "${HAO}" || error "无法创建必要目录"

    # 复制基础文件到内存
    log "复制基础文件到内存..."
    cp ../table/*.txt "${HAO}" || error "复制码表文件失败"
    cp ../template/*.yaml ../template/*.txt "${HAO}" || error "复制模板文件失败"
    cp -r ../template/lua "${HAO}/lua" || error "复制 Lua 脚本失败"
    cp -r ../template/opencc "${HAO}/opencc" || error "复制 OpenCC 配置失败"
    cp -r ../template/hao "${HAO}/hao" || error "复制码表文件失败"
    # 使用自定义配置覆盖默认值
    if [ -d "${NAME}" ]; then
        log "应用自定义配置..."
        cp -r "${NAME}"/*.txt "${HAO}"
        cat "${NAME}"/short_sy.txt >> "${HAO}"/hao/leosy.short.dict.yaml
        cat "${NAME}"/quicks_sy.txt >> "${HAO}"/hao/leosy.quicks.dict.yaml
    fi

    # 生成映射表
    log "生成映射表..."
    cat "${HAO}/map_xi.txt" | python ../assets/gen_mappings_table.py >"${HAO}/mappings_table_xi.txt" || error "生成淅码映射表失败"
    cat "${HAO}/map_sy.txt" | python ../assets/gen_mappings_table.py >"${HAO}/mappings_table_sy.txt" || error "生成松烟映射表失败"

    # 生成淅码码表
    log "生成淅码码表..."
    ./gen_xi -q \
        -d "${HAO}/hao_div.txt" \
        -s "${HAO}/simp_xi.txt" \
        -m "${HAO}/map_xi.txt" \
        -b "${HAO}/hao_stroke.txt" \
        -f "${HAO}/freq.txt" \
        -w "${HAO}/cjkext_whitelist.txt" \
        -c "${HAO}/char_xi.txt" \
        -u "${HAO}/fullcode_xi.txt" \
        -o "${HAO}/div_xi.txt" \
        || error "生成淅码码表失败"
    
    log "生成松烟码表..."
    ./gen_sy -q \
        -d "${HAO}/hao_div.txt" \
        -s "${HAO}/simp_xi.txt" \
        -m "${HAO}/map_sy.txt" \
        -b "${HAO}/hao_stroke.txt" \
        -f "${HAO}/freq.txt" \
        -w "${HAO}/cjkext_whitelist.txt" \
        -c "${HAO}/char_sy.txt" \
        -u "${HAO}/fullcode_sy.txt" \
        -o "${HAO}/div_sy.txt" \
        || error "生成松烟码表失败"

    # 生成单字fix全码表
    pushd ${WD}/../assets/simpcode || error "无法切换到 simpcode 目录"
        python genfullcode_xi.py || error "生成单字fix全码表失败"
        python genfullcode_sy.py || error "生成单字fix全码表失败"
    popd

    # 合并码表文件
    log "合并码表文件..."
    pushd ${HAO}/ || error "无法切换到临时目录"
        awk '/单字全码/ {system("cat fullcode_xi_modified.txt"); next} 1' hao/leoxi.full.dict.yaml > temp && mv temp hao/leoxi.full.dict.yaml
        cat div_xi.txt | sed "s/(/[/g" | sed "s/)/]/g" >>"leoxi_chaifen.dict.yaml"
        awk '/单字全码/ {system("cat fullcode_sy_modified.txt"); next} 1' hao/leosy.full.dict.yaml > temp && mv temp hao/leosy.full.dict.yaml
        cat div_sy.txt | sed "s/(/[/g" | sed "s/)/]/g" >>"leosy_chaifen.dict.yaml"
    popd

    #realpath ${HAO}
    #ls -alh ${HAO}/
    #head -n5 ${HAO}/div_xi.txt

    # 生成简码
    log "生成简码..."
    #if ! conda activate rime; then
    #    error "无法激活 conda 环境"
    #fi
    
    # 创建简码生成所需的目录结构
    mkdir -p "${HAO}/simpcode"
    cp -r ../assets/simpcode/pair_equivalence.txt "${HAO}/simpcode/"
    
    # 检查必要文件是否存在
    for f in "${HAO}/hao/leoxi.full.dict.yaml" "${HAO}/freq.txt"; do
        if [ ! -f "$f" ]; then
            error "缺少必要的文件: $f"
        fi
    done
    
    # 运行简码生成脚本
    pushd ${WD}/../assets/simpcode || error "无法切换到 simpcode 目录"
        python simpcode.py || error "生成简码失败"
        awk '/单字标记/ {system("cat res.txt"); next} 1' ${HAO}/hao/leoxi.short.dict.yaml > ${HAO}/temp && mv ${HAO}/temp ${HAO}/hao/leoxi.short.dict.yaml
        #awk '/单字全码/ {system("cat ../gendict/data/单字全码表_modified.txt"); next} 1' ${HAO}/dicts/llama.dict.yaml > ${HAO}/temp && mv ${HAO}/temp ${HAO}/dicts/llama.dict.yaml
    popd

    # 生成跟打词提
    log "生成跟打词提..."
    export INPUT_DIR="${HAO}"
    export OUTPUT_DIR="${HAO}"
    bash ../assets/gen_genda.sh || error "生成跟打词提失败"

    # 生成大竹词提
    log "生成大竹词提..."
    export INPUT_DIR="${HAO}"
    export OUTPUT_DIR="${HAO}"
    bash ../assets/gen_dazhu.sh || error "生成大竹词提失败"

    # 将最终文件复制到目标目录
    log "复制最终文件到目标目录..."
    mkdir -p "${SCHEMAS}/${NAME}"
    
    # 使用rsync进行选择性复制，排除指定文件
    rsync -a --exclude='/gendict' \
              --exclude='/simpcode' \
              --exclude='/多字词.txt' \
              --exclude='/char*.txt' \
              --exclude='/cjkext_whitelist.txt' \
              --exclude='/div*.txt' \
              --exclude='/freq*.txt' \
              --exclude='/fullcode*.txt' \
              --exclude='/hao_*.txt' \
              --exclude='/map_*.txt' \
              --exclude='/simp_*.txt' \
              --exclude='/quicks_*.txt' \
              --exclude='/short_*.txt' \
              --exclude='/roots_*.txt' \
              --exclude='/llama_personal.txt' \
              "${HAO}/" "${SCHEMAS}/${NAME}/" || error "复制文件失败"

    # 删除临时目录
    log "删除临时目录、文件..."
    rm -rf "${RAMDISK}"
    rm -rf "${SCHEMAS}/${NAME}/llama_smart_temp.dict.yaml"

    # 打包发布
    log "打包发布文件..."
    pushd "${SCHEMAS}" || error "无法切换到发布目录"
        #tar -cf - \
        #    --exclude="*userdb" \
        #    --exclude="sync" \
        #    --exclude="*.custom.yaml" \
        #    --exclude="installation.yaml" \
        #    --exclude="user.yaml" \
        #    --exclude="squirrel.yaml" \
        #    --exclude="weasel.yaml" \
        #    --exclude="leoxi.txt" \
        #    "./${NAME}" | \
        #    zstd -9 -T0 -c \
        #    > "releases/${NAME}-${REF_NAME}.tar.zst" \
        #    || error "打包失败"
        zip -9 -r -q "releases/${NAME}-${REF_NAME}.zip" "./${NAME}" \
            -x "*/*userdb*" \
            -x "*/sync/**" \
            -x "*.custom.yaml" \
            -x "*installation.yaml" \
            -x "*user.yaml" \
            -x "*squirrel.yaml" \
            -x "*weasel.yaml" \
            -x "*leoxi.txt" \
            || error "打包失败"
    popd
    log "方案 ${NAME} 生成完成"
}

# 主程序
log "开始部署好码输入法..."
gen_schema hao || error "生成好码方案失败"
log "部署完成"
