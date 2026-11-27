#!/usr/bin/env python3
"""Minimal kernel table-read benchmarks: def file (compiled once to .olean) + probe files.

Pivot question: seconds per kernel read of a 209010-entry table, per representation.

Reps (same 209010 integers from certificate/kernel_lower.bin, except A which is the shape only):
  A  arrayFn  Array.ofFn over a cheap computed cell      (the shape of kTabArray)
  B  arrLit   flat Array literal #[...]                  (needs maxRecDepth ~2e5; flat size only)
  C  ifChain  def fC k := if k = 0 then v0 else if ...   (needs maxRecDepth ~2e5; flat size only)
  D  chunked  Array of 205 Array-literals of 1024 cells, dispatch i/1024 then i%1024
  E  bigNat   Array of 205 Nat literals (1024 cells x 28 bits), shift+mask

Probe theorem: `<access i> = <value> := by decide +kernel`  (kernel, not compiler)
Marginal kernel cost = (t(N2) - t(N1)) / (N2 - N1), def and imports paid once.
"""
import os, struct, sys, random
from pathlib import Path

PLAY = Path(__file__).resolve().parent.parent
UP = Path(os.environ.get("KNAUSGARD_UPSTREAM", str(PLAY / "upstream")))
OUT = PLAY / "bench"
(OUT / "defs").mkdir(parents=True, exist_ok=True)
(OUT / "probes").mkdir(parents=True, exist_ok=True)
(OUT / "olean").mkdir(parents=True, exist_ok=True)

VALS = list(struct.unpack("<209010I", (UP / "certificate" / "kernel_lower.bin").read_bytes()))
N = len(VALS)
BITS, CH = 28, 1024
MASK = (1 << BITS) - 1
assert N == 209010 and max(VALS) <= MASK


def cell(k):
    return (k * 7919 + 104729) % 268435456


def probes(n, lo=0, hi=N):
    if n == 0:
        return []
    return sorted(random.Random(20261107).sample(range(lo, hi), n))


HDR = "set_option maxHeartbeats 0\n"

DEFS = {
    "A": HDR + "def cellI (k : Nat) : Nat := (k * 7919 + 104729) % 268435456\n"
               "def tabA : Array Nat := Array.ofFn (n := 209010) fun k => cellI k\n",
    "B": HDR + "set_option maxRecDepth 400000\n"
               "noncomputable def tabB : Array Nat := #[" + ", ".join(map(str, VALS)) + "]\n",
    "C": HDR + "set_option maxRecDepth 400000\n"
               "def fC (k : Nat) : Nat :=\n"
         + "".join(f"  if k = {i} then {v} else\n" for i, v in enumerate(VALS)) + "  0\n",
    "D": HDR + "set_option maxRecDepth 4000\nnoncomputable def tabD : Array (Array Nat) := #[\n  "
         + ",\n  ".join("#[" + ", ".join(map(str, VALS[c:c + CH])) + "]" for c in range(0, N, CH))
         + "\n]\nnoncomputable def getD (i : Nat) : Nat := (tabD[i / 1024]!)[i % 1024]!\n",
    "E": HDR + "def natChunk : Nat → Nat\n"
         + "".join("  | %d => 0x%s\n" % (c // CH, format(sum(v << (BITS * j) for j, v in enumerate(VALS[c:c + CH])), "x"))
                   for c in range(0, N, CH))
         + "  | _ => 0\ndef getE (i : Nat) : Nat := (natChunk (i / 1024) >>> (28 * (i % 1024))) &&& 268435455\n",
}

ACCESS = {"A": ("tabA[{i}]!", cell), "B": ("tabB[{i}]!", VALS.__getitem__),
          "C": ("fC {i}", VALS.__getitem__), "D": ("getD {i}", VALS.__getitem__),
          "E": ("getE {i}", VALS.__getitem__)}


def probe_file(rep, n, lo=0, hi=N):
    tmpl, val = ACCESS[rep]
    out = [f"import Rep{rep}\n" + HDR + "set_option maxRecDepth 1000000\n"]
    for k, i in enumerate(probes(n, lo, hi)):
        out.append(f"theorem p{rep.lower()}{k} : {tmpl.format(i=i)} = {val(i)} := by decide +kernel\n")
    return "".join(out)


if __name__ == "__main__":
    what, rep = sys.argv[1], sys.argv[2]
    if what == "def":
        (OUT / "defs" / f"Rep{rep}.lean").write_text(DEFS[rep])
        print(OUT / "defs" / f"Rep{rep}.lean")
    else:
        n = int(sys.argv[3])
        lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        hi = int(sys.argv[5]) if len(sys.argv) > 5 else N
        tag = "" if (lo, hi) == (0, N) else f"_i{lo}-{hi}"
        f = OUT / "probes" / f"rep{rep}_{n}{tag}.lean"
        f.write_text(probe_file(rep, n, lo, hi))
        print(f)
