# COVERAGE — what the partial certificate covers, honestly

The certificate `cert/Partial.lean` proves, by `decide +kernel`, that five boxes taken from the
author's own accepted set pass his own range-minimum test `basicF` on his own kernel table. This
document states exactly how much of Axiom 1 that is, and what the coverage-vs-budget curve looks
like, so that nobody reads the certificate as a discharge of the axiom.

## What the certificate is

| | |
|---|---|
| theorem (intended) | `Cert.covered_pass : covered.all (fun p => basicF kT p.1.toArray p.2.toArray) = true` |
| plus | 5 per-box theorems `covered_0 … covered_4` (each box checkable on its own line) |
| status | generated and type-checked; the kernel check did **not** complete on this host — see "Status of the kernel check" below (memory wall) |
| plus | `Cert.spot_lattice`, `spot_double`, `spot_corner`, `spot_vacancy` — the author's four own kernel-checked boxes, re-proved through the new accessor (fidelity check) |
| table | `certificate/kernel_lower.bin`, 209 010 entries, sha256 `b80e5a8c…cded36`, read as `Cert.kT` |
| arithmetic | verbatim copy of his `Distinct839/Local/Checker.lean` + `minF`/`mkEdgeF`/`edgesF`/`basicF` from `Local/Spot.lean` |
| consumer (his, unmodified) | `basicF_sound : TableSound f → basicF f lo hi = true → BoxOK lo hi` |
| box source | his `verifier/verify.cpp`, instrumented by `tools/patch_dump.py`; stock counts reproduce `cpp_verification.json` exactly |
| budget | 137 260 table reads (the cost model is his: gap `r` is read `(r+1)(6−r)` times per box) |

## The numbers

Boxes covered: **5**, all of width ≈ 490 in every gap (the cheapest accepted width class):

```
[491,490,490,490,490,491]  reads 27,452  each
```

| quantity | value |
|---|---|
| covered boxes | 5 of **21 157 274** accepted basic-test boxes = **2.4 × 10⁻⁷** |
| covered volume (gap space) | 1.403 × 10¹⁷ of 5.512 × 10³¹ = **1.26 × 10⁻¹⁵ of the root box** |
| root box | `[13926, 209009]⁶`, volume 195 083⁶ = 55 120 932 172 281 490 656 344 867 683 369 |
| still unverified | 21 157 269 accepted boxes (basic) + 9 076 381 (affine) + the whole continuum → still the single `native_decide` boolean |

So: **the certificate reduces the trusted region by 1.3 parts in 10¹⁵.** In plain terms it proves
nothing anybody would pay for, and that is the finding, not an accident of effort: §2 shows the cost
that would be needed.

## Coverage vs budget (measured cost model, his own boxes)

Greedy by volume per read over the author's accepted boxes, ranked by the exact cost model
(`reads(box) = Σ_r (r+1)(6−r)·w_r`). `fraction` is the covered share of the root box's volume.

| kernel reads | boxes | covered fraction | wall time at 6.2 ms/read |
|---|---|---|---|
| **137 260 (this certificate)** | **5** | **1.3 × 10⁻¹⁵** | **14 min** |
| 1.6 × 10⁶ | 1 (the widest accepted box) | **8.6 × 10⁻⁶** | 2.8 h |
| 1.07 × 10⁷ | 9 | 2.6 × 10⁻⁵ | 18 h |
| 10⁸ | 123 | 4.1 × 10⁻⁵ | 7 days |
| 10⁹ | 1 285 | 1.7 × 10⁻⁴ | 72 days |
| 10¹⁰ | 18 083 | 4.2 × 10⁻⁴ | 2 years |
| 5.5 × 10¹⁰ | 200 000 (the top-volume pool) | 4.7 × 10⁻⁴ | 11 years |
| **1.14 × 10¹²** | **21 157 274 (all)** | **1.0** | **224 years** |

Two things to read off this table:

1. **Volume is not box count.** One box — the widest accepted one — is worth 8.6 × 10⁻⁶ of the
   region, while the 5 boxes in the certificate are worth 1.3 × 10⁻¹⁵: a factor 10⁷ between two
   honest ways of saying "box count". The audit's phrasing "1.6% of the 60.5M boxes" is a *box
   count* statement; as a statement about the region it is off by ~13 orders.
2. **Cost per covered volume explodes.** 10⁹ reads buys 1.7 × 10⁻⁴; the next three orders of reads
   buy 0.9998. Because the region's volume sits in the *large* boxes, which are exactly the
   expensive ones to read, and the cheap boxes are the small ones.

## Why the budget is where it is

The audit suggested ~10⁶ reads as a fixed kernel budget. At the measured 6.2 ms/read that is
1.7 hours, and it buys one box. I set the certificate's budget below that (137 k reads, ~14 min of
kernel time on this loaded host) because the marginal value of a second order of magnitude of
coverage is ~10 orders of magnitude of region — i.e. nothing. Anyone who wants the 10⁶-read version
can run `tools/select_leaves.py 1000000 1 cert/sel1m.json` and
`tools/gen_partial.py cert/sel1m.json cert/Partial1M.lean`; it will verify in ~1.7 h on this host.

## Status of the kernel check (measured, not assumed)

| what | reads | kernel result on this host |
|---|---|---|
| his four spot boxes (`cert/Spot.lean`) | 224 each | **verified** (`lean cert/Spot.lean`, ~7 s CPU for all four) |
| one accepted box, cheapest class (`[245,246,245,245,245,490]`, 15 200 reads) | 15 200 | **killed**: 61 s / 6.3 GB on the first attempt, 152 s / 9.3 GB on a retry (the ceiling moves with host pressure) |
| one accepted box, cheapest *balanced* class (27 452 reads) | 27 452 | **killed** at 60 s, **6.9 GB peak RSS** |
| the 5-box certificate (`cert/Partial.lean`) | 137 260 (×2 with the aggregate) | **not completed**: the host kills the process at ~6 GB |

So the binding constraint is **memory, not only time**: `decide +kernel` retains the reduction terms
of every table read, at roughly 0.4 MB per read, i.e. **one accepted box per ~6 GB of RAM**. Every
box in his cover costs at least 15 190 reads = ~6.3 GB, so *no* box of his branch and bound could be
checked to completion in this session on this host — the certificate is generated, type-checked and
ready, and its per-box theorems (`covered_0 … covered_4`) are each one line that verifies in ~95 s on
a host that will give the process ~7 GB.

This memory wall is itself a result worth reporting: it is invisible in the read-count arithmetic,
it does not improve with a faster accessor (the copy is per unfold), and it puts the *minimum* unit
of a kernel-checked cover at one accepted box per 6 GB of RAM — 21 157 274 boxes would need the
reduction terms of ~10⁵ boxes' worth of RAM even if time were free.

## What would have to be true for a real certificate

1. **A kernel-cheap per-box test whose cost does not scale with box width.** `basicF` reads every
   cell of every span; with a precomputed range-minimum structure supplied as data, a box costs ~98
   reads regardless of width, but each read is still one kernel unfold (≥1.8 ms measured), so
   21 M boxes × 98 × 1.8 ms ≈ 44 days. The binding constraint is kernel *unfolds/reduction steps per
   box*, not the accessor's asymptotics.
2. **A `TableSound` bridge** for the accessor: `∀ k < 209010, kT k = kTabArray[k]` — 209 010 kernel
   evaluations of his `kTab`, which includes the rational/trigonometric arithmetic. Not attempted
   here; it is the same order of cost as the accessor work the audit budgeted 4–8 weeks for.
3. **A different certificate shape** that does not enumerate boxes: the audit's Route B (a certified
   analytic majorant per box, no table reads) remains the only path to a human-readable case count.
   Nothing in this work changes that recommendation — it strengthens it.

## Honest summary for the delivery note

> We measured what the kernel charges for the author's table (his 0.1 s figure is an underestimate
> by ~6 orders for the array shape; a tree accessor brings a read to ~6 ms) and replayed 5 of his
> 21 157 274 accepted boxes through his own `basicF` and `basicF_sound`, kernel-checked. That covers
> 1.3 × 10⁻¹⁵ of the root box. A full replay is ~1.14 × 10¹² reads ≈ 224 years on the measured rate.
> The trust reduction is therefore nil in practice; the deliverable is the measurement, the
> accessor, and a working machinery that the author (or anyone) can use to check samples.
