# BENCHMARK — the pivotal measurement: what one kernel table read costs

The audit (`../knausgard-audit/CERT_DESIGN.md` §2–3) reduced the whole certificate programme to one
unknown number: **seconds per kernel read of the 209010-entry table**. At the paper's figure (0.1 s)
a full kernel replay of Axiom 1 costs ~5 years; the audit projected ~28 minutes if a better accessor
brought the read to ~1 µs. This document measures it.

**Verdict in one line:** the 10⁵ *ratio* is real — the accessor delta from the shipped shape to the
best kernel-cheap shape is ~10⁸ — but the *absolute floor* is ~6 ms per read on this machine, not
1 µs, and the real cover has ≥14 000 reads per accepted box (not 56), so **a full kernel replay
stays at ~10² years and Route A as projected does not close.** The partial certificate is therefore
the only artifact that exists, and its coverage is reported honestly in `COVERAGE.md`.

## 1. What was measured, and how

All numbers are **CPU seconds** (`user`+`sys` of `/usr/bin/time -p`), not wall clock, because the
host was running other agents' Lean builds throughout (load average 180–450 — see §7). Each figure
is the *marginal* cost: a file of `n` probe theorems minus the same file with `n = 0`, divided by
`n`. Probes are of the form

```lean
theorem p_k : <accessor> <index> = <expected value> := by decide +kernel
```

so the reduction is performed by **the kernel**, exactly as in the author's own spot checks
(`Distinct839/Local/SpotChecks.lean`, `basicF_sound … (by decide +kernel)`). A deliberately wrong
probe was used as a control in every representation: it fails (`decide proved that the proposition
… is false`), which proves the reduction is actually executed and not skipped.

Toolchain: Lean `v4.33.0-rc2` (`~/.elan/toolchains/leanprover--lean4---v4.33.0-rc2`), the version
his `lean/README.md` names for the development. Data: `certificate/kernel_lower.bin` from
`github.com/kristianmk/839` @ `b280d51bef5ab32b3280b0955d040085ed522d59`, 209010 little-endian
`uint32`, sha256 `b80e5a8c…cded36` = `inputs.json → table_sha256` (verified). Scripts:
`tools/gen_bench.py`, `tools/gen_G.py`, `tools/measure.py`; probes in `bench/probes/`.

## 2. Results — seconds per kernel read of the *same* 209010 values

| # | representation of the table | per read | note |
|---|---|---|---|
| **A** | `Array.ofFn (n := 209010) (fun k => cell k)` — **the shape of his `kTabArray`** | **not measurable: >900 s**, process killed | quadratic: marginal cost at n=512 is 3.2 s and at n=1024 is 16.4 s (×4.9 per doubling ⇒ Θ(n^2.0–2.3)), so at n=209010 it is **5×10⁵ – 3×10⁶ s (6–37 days) per read**. `Array.ofFn` is `go` with `acc.push`, and in the kernel `push` is list-append ⇒ the whole array is rebuilt per read |
| **B/D** | flat `Array` literal `#[…209010…]`, and the same chunked as `Array (Array Nat)` | **~12 MB allocated and copied per read** | RSS 404 → 439 → 478 MB over 3 reads. 4000 reads thrashed (4 245 s of `sys`), did not complete. Unfolding a definition copies its value term: one 209010-node literal is copied in full on every read |
| **E** | 205 `Nat` literals of 1024 cells × 28 bits, `(chunk >>> 28*j) &&& mask` | **4.9 ms** | a `Nat` literal is one term node, so unfolding is free — but the shift is `Nat.div` in the kernel |
| **G** | tree of **named** definitions, 64 × 64 × 52 (the "segmented literals" the audit proposed) | **10.3 ms** standalone, **6.2 ms** in the certificate context | 3 unfolds + ~180 list steps; 896 reads (his 4 spot boxes) took 5.6 s |
| (m_b) | single named definition holding a 64-element list | 1.2 ms | 1 unfold + ≤64 steps — the floor for this family |

Accessor delta, shipped → best: ≥5×10⁵ s ÷ 6×10⁻³ s ≈ **≥8×10⁷** (using the conservative quadratic fit; 5×10⁸ with the n^2.3 fit). The audit's hoped-for 10⁵ factor
is real *as a ratio*; it is the absolute number that misses.

Calibration of the underlying rate: an `n`-step kernel recursion (`def dbl`) costs 17 µs per step on
this host (20 000 steps = 0.34 s marginal). At that rate a 64-step list walk is 1.1 ms and a
180-step tree walk is 3 ms, which is what §2 measures — the figures are internally consistent.

## 3. The second correction: reads per leaf is ≥14 000, not 56

`basicF` reads, for each of the 21 pairs, every cell of that pair's distance span. Gap `r` is read
`(r+1)(6−r)` times, so

```
reads(box) = Σ_r (r+1)(6−r) · w_r      (= 56 · w when all six widths are equal)
```

The audit multiplied 56 by the leaf count, i.e. it assumed terminal leaves of width 1. His search
never accepts one: instrumenting his own verifier (`tools/patch_dump.py`, stock counters reproduced
exactly) shows every accepted box has **max width ≥ 256**, because the affine test exists precisely
to settle boxes of width ≤ 512 and the basic test settles the rest. The accepted set is
21 157 274 boxes (basic/span test) + 9 076 381 (affine test).

So the honest arithmetic for a kernel replay of the basic-test half is (computed exactly over his
own accepted set, `cert/replay_cost.txt`):

```
accepted basic-test boxes                     21,157,274
reads for the whole accepted cover         1,142,293,396,938   (~1.14 × 10¹²)
reads per box: min 15,190 · median 36,270 · mean 53,991 · max 1,599,524
```

Both corrections push the same way: the audit's 5.4 years was optimistic by ~3 orders in reads
(56 vs ≥15,190 per box) and ~16× in per-read cost (0.1 s vs 6.2 ms measured) — while being
pessimistic by ~10⁸ in accessor cost. Its net "~28 minutes at 1 µs/read" is wrong by ~4 orders of
magnitude. Note also that no accepted box is narrow: min max-width 490, max 31,364.

The binding constraint is not the accessor's asymptotics but **kernel reduction steps per box**:
even a hypothetical certificate that settled a box in ~100 reduction steps (with a precomputed
range-minimum structure, ~98 reads/box) would cost ≥ 98 × 1.8 ms ≈ 0.18 s per box, i.e. ~44 days
for 21 M boxes — before any table soundness bridge. Nothing in the accessor work reaches that.

## 4. What the accessor work *is* good for

The tree-of-named-definitions accessor (`Cert/Table.lean`, generated from the author's table) is
what makes any kernel check of this table possible at all: his shipped `kTabArray` cannot be read by
the kernel in any practical time (≥5×10⁵ s per read), whereas `Cert.kT` reads in ~6 ms. That is
enough to check **samples and individual boxes** — which is exactly what his spot checks do — and
not enough to check 21 million of them.

It also settles the audit's decisive open question in the negative: *"a proper accessor may be 10⁵×
cheaper"* — cheaper, yes (10⁸ at the shape level); **cheap enough for a full replay, no** (the floor
is ms, not µs, and `TableSound` bridging plus 21 M boxes stay out of reach).

## 5. Consequences for the certificate programme

| quantity | value |
|---|---|
| per read, shipped `kTabArray` shape | >900 s measured (killed); 5×10⁵–3×10⁶ s fitted from n=512, 1024 |
| per read, best kernel-cheap accessor built here | 6.2×10⁻³ s (loaded host) |
| reads for the basic-test half of the cover | 1.14×10¹² (exact, his own accepted boxes) |
| full replay at 6.2 ms/read | ≈224 years |
| full replay at 0.3 ms/read (20× faster host) | ≈10.9 years |
| full replay at 1 µs/read (audit assumption) | ≈13 days — **not achievable with any representation measured here** |
| what a 10⁶-read budget buys | ≈66 accepted boxes out of 21 157 274 (≈3×10⁻⁶ of them, and of the volume) |

## 6. Bearing on the other two axioms

Axiom 2 (Simple673) has 8 points → 28 pairs, `Σ_{i<j}(j−i) = 84` reads per unit width, a 262 145-entry
table, and 267 666 082 accepted boxes (`checkAllPar`, 96 chunks). Axiom 3 (Line889) has 6 gaps,
56 reads per unit width, a 262 145-entry table, 286 479 727 accepted boxes. Both are strictly worse
than Axiom 1 (larger table, more accepted boxes). Nothing in §2–§5 changes favourably for them; the
same accessor would be needed and the same 10²-year wall applies.

## 7. Caveats, stated plainly

1. **The host was loaded** (load average 180–450 from other agents' Lean builds). CPU time is the
   metric, so scheduling does not inflate it, but cache/memory-bandwidth contention does. Expect a
   quiet machine to be perhaps 5–20× faster; the table in §5 shows the conclusion survives a 20×
   speedup, and a 10⁴× speedup would be needed to reach the audit's 28 minutes.
2. **Lemma-elaboration overhead is included** in the marginal figures: a `decide +kernel` theorem
   with a trivial statement costs ~1.5 ms of elaboration here; marginal costs are differences of
   total CPU time, so this cancels only insofar as it is constant — it was measured constant.
3. **Not measured:** the 8-point (Axiom 2) table, the affine test's per-box cost, `native_decide`
   compiled speed, and a truly idle host. The affine test reads no range minima, so its per-box cost
   is a different (probably larger) number — the 9 076 381 affine-accepted boxes are excluded from
   the replay arithmetic, which is therefore a lower bound.
4. The per-read floor was not pushed to its limit: a two-level (205 × 1024) named-def tree or a
   smaller-leaf tree was not tried. Given the measured per-unfold cost (~1.8 ms) and the ~180 steps,
   the plausible best is ~1–2 ms per read — a 3–6× gain on §2, not the 10³ needed.

## 7b. A second wall: memory (found while checking the certificate)

`decide +kernel` retains the reduction terms of every table read until the theorem ends: one accepted
box of the cheapest class (15 200 reads) was killed at **6.3 GB / 61 s** on one attempt and at
**9.3 GB / 152 s** on a retry (the ceiling moves with host memory pressure); the 27 452-read class
needs 7 GB or more. That is ~0.4 MB per read, and it is *not* fixed by a cheaper accessor
(the retention is per unfold). Practical consequence: **one accepted box of his cover per ~6 GB of
RAM**, and no accepted box (min 15 190 reads) could be checked to completion here. His own four spot
boxes (224 reads each) do check — `cert/Spot.lean`, verified.

## 8. Reproduce

```bash
cd ~/bigo-campaign/knausgard-cert
python3 tools/gen_bench.py  def A|B|C|D|E    # definition files
python3 tools/gen_bench.py  probe A 4000     # 4000 kernel reads
lean -o bench/olean/RepA.olean bench/defs/RepA.lean
LEAN_PATH=bench/olean lean bench/probes/repA_4000.lean
python3 tools/gen_G.py def && python3 tools/gen_G.py probe 4000
python3 tools/measure.py G 0,1000,4000       # marginal CPU per read, min of 3
```
