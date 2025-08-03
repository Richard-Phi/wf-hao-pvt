import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python script.py input.txt > output.txt", file=sys.stderr)
    sys.exit(1)

input_file = sys.argv[1]
cnt_map = defaultdict(int)

with open(input_file, "r") as f:
    for line in f:
        code, char = line.strip().split("\t")
        if code.endswith("_"):
            base = code[:-1]
            is_first = True
        else:
            base = code
            is_first = False
        
        count = cnt_map[base]
        
        if count == 0:
            new_code = f"{base}_" if is_first else base
        else:
            n = count - 1
            if n < 4:
                suffix = [";", "'", "4", "5"][n]
            else:
                group = (n - 4) // 5 + 1
                idx = (n - 4) % 5 + 1
                suffix = "=" * group + str(idx)
            new_code = base + suffix
        
        print(f"{new_code}\t{char}")
        cnt_map[base] += 1