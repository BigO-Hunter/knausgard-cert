#!/usr/bin/env python3
"""Rep G: the 'segmented literal' accessor the audit proposed -- a tree of NAMED definitions.

The point: Lean's kernel copies a definition's value term when it unfolds it. A flat 209010-entry
literal is ONE term of 209010 nodes, so every read copies ~12 MB. A tree of named defs makes each
unfold copy only the nodes of that small segment, so a read costs O(depth * segment + log n) small
copies instead of O(n) large ones.

Layout: LEAF = 64 values, MID = 64 x LEAF (4096 values), ROOT = 52 x MID (209010+ values, last short).
"""
import struct, sys
from pathlib import Path

PLAY = Path.home() / "bigo-campaign" / "knausgard-cert"
UP = PLAY / "upstream"
OUT = PLAY / "bench"
VALS = list(struct.unpack("<209010I", (UP / "certificate" / "kernel_lower.bin").read_bytes()))
N = len(VALS)
LEAF, MID = 64, 64
SPAN = LEAF * MID  # 4096


def gen_def():
    s = ["set_option maxHeartbeats 0\n"]
    leaf_idx = []
    for c in range(0, N, LEAF):
        name = f"L{c // LEAF}"
        leaf_idx.append(name)
        s.append(f"def {name} : List Nat := [{', '.join(map(str, VALS[c:c + LEAF]))}]\n")
    mid_idx = []
    for g in range(0, len(leaf_idx), MID):
        name = f"M{g // MID}"
        mid_idx.append(name)
        s.append(f"def {name} : List (List Nat) := [{', '.join(leaf_idx[g:g + MID])}]\n")
    s.append("def ROOT : List (List (List Nat)) := [" + ", ".join(mid_idx) + "]\n")
    s.append(
        "def getG (i : Nat) : Nat :=\n"
        f"  let m := ROOT.getD (i / {SPAN}) []\n"
        f"  let l := m.getD ((i % {SPAN}) / {LEAF}) []\n"
        f"  l.getD (i % {LEAF}) 0\n")
    return "".join(s)


def gen_probes(n, lo=0, hi=N):
    import random
    idx = sorted(random.Random(20261107).sample(range(lo, hi), n)) if n else []
    out = ["import RepG\nset_option maxHeartbeats 0\n"]
    out += [f"theorem pg{k} : getG {i} = {VALS[i]} := by decide +kernel\n" for k, i in enumerate(idx)]
    return "".join(out)


if __name__ == "__main__":
    (OUT / "defs").mkdir(parents=True, exist_ok=True)
    (OUT / "probes").mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "def":
        (OUT / "defs" / "RepG.lean").write_text(gen_def())
        print(OUT / "defs" / "RepG.lean")
    else:
        n = int(sys.argv[2])
        f = OUT / "probes" / f"repG_{n}.lean"
        f.write_text(gen_probes(n))
        print(f)
