#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transform a two‑column TSV file (code<TAB>char) into a new code set.

* 1st occurrence   → keep the original “_” flag (or nothing if it was absent)
* 2nd‑5th occurrences → suffixes ';', ''', '8', '9'
* From the 6th occurrence onward we start *pagination*.
  For each new page we prepend one more “=” to the same five suffixes,
  i.e.  =_, =;, =', =8, =9   then   ==_, ==;, … and so on.

Usage:
    python script.py input.txt > output.txt
"""

import sys
from collections import defaultdict

# ----------------------------------------------------------------------
# Configuration – change only here if the set of suffixes ever needs to be
# different again.
# ----------------------------------------------------------------------
# The five suffixes that appear on every page, **including** the leading
# underscore for the “first‑choice” entry.
PAGE_SUFFIXES = ["_", ";", "'", "8", "9"]          # index 0 = first‑choice

def pagination_suffix(page: int, idx: int) -> str:
    """
    Build the suffix for a paged entry.

    Parameters
    ----------
    page : int
        1‑based page number (page == 1 corresponds to the *second* page of the
        original data, i.e. the first time we need a leading “=”).
    idx : int
        0‑based index inside the page (0 → first‑choice, 1 → second‑choice,
        …, 4 → fifth‑choice).

    Returns
    -------
    str
        Something like  '=_' , '=;' , '=8' , '==_' , '===9' , …
    """
    return ("=" * page) + PAGE_SUFFIXES[idx]


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print(
            "Usage: python script.py input.txt > output.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file = argv[1]
    # How many times we have already emitted a particular *base* code.
    cnt_map: defaultdict[str, int] = defaultdict(int)

    with open(input_file, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            if not line:                     # skip empty lines
                continue

            # Expect exactly one TAB separating the code from the character.
            try:
                code, char = line.split("\t", 1)
            except ValueError:
                print(
                    f"Skipping malformed line (no TAB found): {line!r}",
                    file=sys.stderr,
                )
                continue

            # ------------------------------------------------------------------
            # 1️⃣  Detect the original “_” flag (means “first‑choice” on page 1)
            # ------------------------------------------------------------------
            if code.endswith("_"):
                base = code[:-1]   # strip the trailing underscore
                has_underscore_flag = True
            else:
                base = code
                has_underscore_flag = False

            # How many times have we already emitted this base?
            count = cnt_map[base]

            # ------------------------------------------------------------------
            # 2️⃣  Build the new code according to the occurrence count
            # ------------------------------------------------------------------
            if count == 0:
                # First occurrence – keep the original underscore flag if it existed.
                new_code = f"{base}_" if has_underscore_flag else base
            elif 1 <= count <= 4:          # 2nd – 5th occurrence
                suffix = PAGE_SUFFIXES[count]          # PAGE_SUFFIXES[1] → ';' …
                new_code = base + suffix
            else:
                # Pagination part (6th occurrence and later)
                #   page  = 1 for the *second* page of the original data,
                #   idx   = position inside that page (0‑4)
                zero_based_page_index = (count - 5) // 5   # 0 for page 2, 1 for page 3, …
                page = zero_based_page_index + 1          # make it 1‑based for the "=" count
                idx  = (count - 5) % 5
                new_code = base + pagination_suffix(page, idx)

            # Emit the transformed line
            print(f"{new_code}\t{char}")

            # Record that we have now output one more instance of this base.
            cnt_map[base] += 1


if __name__ == "__main__":
    main()
