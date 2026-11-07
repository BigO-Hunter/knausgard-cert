#!/usr/bin/env python3
"""Measure marginal kernel cost of N table reads. Reports user+sys CPU seconds (min of REPS)."""
import subprocess, sys, os, time, json
from pathlib import Path

PLAY = Path.home() / "bigo-campaign" / "knausgard-cert"
ENV = dict(os.environ, LEAN_PATH=str(PLAY / "bench" / "olean"))


def cpu_of(path, reps=3):
    best = None
    for _ in range(reps):
        p = subprocess.run(["/usr/bin/time", "-p", "lean", str(path)],
                           capture_output=True, text=True, env=ENV)
        if p.returncode != 0:
            raise SystemExit(f"FAILED {path}:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
        u = s = None
        for line in p.stderr.splitlines():
            if line.startswith("user"):
                u = float(line.split()[1])
            elif line.startswith("sys"):
                s = float(line.split()[1])
        t = u + s
        best = t if best is None else min(best, t)
    return best


if __name__ == "__main__":
    rep = sys.argv[1]
    ns = [int(x) for x in sys.argv[2].split(",")]
    res = {}
    for n in ns:
        f = PLAY / "bench" / "probes" / f"rep{rep}_{n}.lean"
        if not f.exists():
            subprocess.run([sys.executable, str(PLAY / "tools" / "gen_bench.py"), "probe", rep, str(n)],
                           check=True, capture_output=True)
        res[n] = cpu_of(f)
        print(f"{rep} n={n:>7}  cpu={res[n]:.3f}s", flush=True)
    ks = sorted(res)
    if len(ks) >= 2:
        lo, hi = ks[0], ks[-1]
        d = (res[hi] - res[lo]) / (hi - lo)
        print(f"{rep}: marginal CPU per kernel read = {d*1e6:.3f} us  "
              f"({d:.3e} s)  at mean index ~1.0e5")
    (PLAY / "bench" / f"measure_{rep}.json").write_text(json.dumps(res, indent=2))
