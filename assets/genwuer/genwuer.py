from typing import Dict, List, Tuple


码表: List[Tuple[str, str, str]] = []
with open('../simpcode/res.txt', encoding='utf-8') as f:
    for line in f:
        字, 码, 频 = line.strip().split('\t')
        码表.append([字, 码, 频])
        if len(码) > 2:
            码表.append([字, ';' + 码, 频])

with open('../../schemas/hao/hao/hao.xi.dynamic.dict.yaml', 'w', encoding='utf-8') as f:
    f.write('#Rime dictionary\n\nname: hao.xi.dynamic\nversion: "0"\ncolumns:\n  - text\n  - code\n  - weight\nsort: original\n...\n\n\n' + '\n'.join([f'{字}\t{码}\t{频}' for 字, 码, 频 in 码表]))

reverse = {}
for 字, 码, 频 in 码表:
    # 只保留码长为1~4且不以分号开头的码
    if 1 <= len(码.replace(';', '')) <= 4 and not 码.startswith(';'):
        if 码 not in reverse:
            reverse[码] = 字  # 只保留第一个字

output = []
for 码, 字 in reverse.items():
    output.append(f'{码}\t{字}')

with open('../../schemas/hao/hao_xi_52p.fixed.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))