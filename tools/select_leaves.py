#!/usr/bin/env python3
"""Choose the certificate's boxes from the author's own accepted boxes, and build the coverage curve.

Source: /tmp/leaves_all.txt -- every box his reference verifier accepted with the span or basic test
(21,157,274 lines, from his verify.cpp instrumented by tools/patch_dump.py; stock counts match
certificate/cpp_verification.json exactly).

Cost model (his own, not a guess): `basicF` reads, for each of the 21 pairs, the cells of the pair's
distance span. Summed over pairs, gap r is read (r+1)(6-r) times, so
    reads(box) = sum_r (r+1)(6-r) * (hi_r - lo_r)      [= 56 * sum_r w_r when all widths are equal]
Covered volume (gap space) = prod_r (hi_r - lo_r); root box = (209009 - 13926)^6.

Two products, one pass:
  * certificate: greedy by volume/read among boxes with reads <= budget/min_boxes, so at least
    min_boxes boxes fit the budget;
  * coverage curve: greedy by volume/read over the whole pool, reported at the read budgets below
    (this is "what would X kernel reads buy", independent of what we can check today).

Usage: python3 select_leaves.py <budget_reads> <min_boxes> <out.json> [leaves]
"""
import sys, json, heapq
from pathlib import Path

COEF = [(r + 1) * (6 - r) for r in range(6)]
SIDE = 209009 - 13926
ROOT_VOL = SIDE ** 6
CURVE = [10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8, 10 ** 9, 10 ** 10, 10 ** 11, 10 ** 12]
KCURVE = 200000
KCERT = 5000


def main():
    budget, min_boxes = int(sys.argv[1]), int(sys.argv[2])
    out = Path(sys.argv[3])
    src = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("/tmp/leaves_all.txt")
    cap = max(budget // max(1, min_boxes), 1)
    heap_c, heap_k = [], []
    total = 0
    wh = {}
    with src.open() as f:
        for line in f:
            v = [int(x) for x in line.split()]
            if len(v) != 12:
                continue
            lo, hi = v[:6], v[6:]
            w = [hi[r] - lo[r] for r in range(6)]
            if min(w) <= 0:
                continue
            reads = sum(COEF[r] * w[r] for r in range(6))
            vol = 1
            for x in w:
                vol *= x
            total += 1
            wh[max(w)] = wh.get(max(w), 0) + 1
            ratio = vol / reads
            item = (ratio, reads, vol, lo, hi, w)
            if len(heap_k) < KCURVE:
                heapq.heappush(heap_k, item)
            elif ratio > heap_k[0][0]:
                heapq.heapreplace(heap_k, item)
            if reads <= cap:
                if len(heap_c) < KCERT:
                    heapq.heappush(heap_c, item)
                elif ratio > heap_c[0][0]:
                    heapq.heapreplace(heap_c, item)
    cand_c = sorted(heap_c, reverse=True)
    chosen, used = [], 0
    for ratio, reads, vol, lo, hi, w in cand_c:
        if used + reads > budget:
            continue
        chosen.append({"lo": lo, "hi": hi, "widths": w, "reads": reads, "volume": vol})
        used += reads
    cand_k = sorted(heap_k, reverse=True)
    curve, cv, cr, cb, marks = [], 0, 0, 0, sorted(CURVE)
    for ratio, reads, vol, lo, hi, w in cand_k:
        cr += reads
        cv += vol
        cb += 1
        while marks and cr >= marks[0]:
            curve.append({"reads": cr, "boxes": cb, "volume": cv, "fraction": cv / ROOT_VOL})
            marks.pop(0)
    for m in marks:
        curve.append({"reads": cr, "boxes": cb, "volume": cv, "fraction": cv / ROOT_VOL,
                      "note": f"pool of {KCURVE} exhausted at {m} reads"})
    covered = sum(c["volume"] for c in chosen)
    res = {
        "root_side": SIDE, "root_volume": ROOT_VOL, "pool_size": total,
        "accepted_max_width_histogram": dict(sorted(wh.items())),
        "budget_reads": budget, "min_boxes": min_boxes, "cap_reads_per_box": cap,
        "used_reads": used, "boxes": len(chosen),
        "covered_volume": covered, "covered_fraction": covered / ROOT_VOL,
        "covered_box_fraction": len(chosen) / total,
        "coverage_curve": curve, "chosen": chosen,
    }
    out.write_text(json.dumps(res, indent=1))
    print(f"pool {total:,}  cap {cap:,}  chosen {len(chosen)} boxes  reads {used:,}/{budget:,}  "
          f"volume {covered/ROOT_VOL:.3e}  boxcount {len(chosen)/total:.2e}")
    print("widths:", [c["widths"] for c in chosen])
    for c in curve:
        print(f"  reads {c['reads']:>16,}  boxes {c['boxes']:>8,}  fraction {c['fraction']:.3e}  "
              f"{c.get('note','')}")


if __name__ == "__main__":
    main()
