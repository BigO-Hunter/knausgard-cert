# DELIVERY_DRAFT — note to `kristianmk/839`  (DRAFT — not posted, not sent)

Subject: a measured kernel cost for the three `native_decide` axioms, and an Axiom-1 partial certificate

---

Dear Dr Knausgård,

I have been auditing the three computation-axioms of your paper *"More than 83.9% of the zeros of the
Riemann zeta function are distinct and more than 67.35% are simple and on the critical line"*
(arXiv:2610.08965) against the repository `kristianmk/839` at commit `b280d51b`. Two things came out
of it that I think are worth your time: a measurement that corrects a number in your source, and a
kernel-checked partial certificate that uses your own `basicF_sound`. **Your theorem stands as
published** — nothing below weakens it, and nothing was posted anywhere public.

## 1. Your remark "about 0.1 s per table entry" is an underestimate, and I can say why

`Distinct839/Local/Spot.lean` says the kernel cannot evaluate the table because "the table has
209010 entries, each costing the kernel about 0.1 s, and kernel arrays are lists". I tried to
measure that number exactly, with `decide +kernel` on representations of the same 209010 values
(`certificate/kernel_lower.bin`, sha256 `b80e5a8c…cded36`, verified).

On your shipped representation — `Array.ofFn (n := tabR + 1) (fun k => kTabWith trigCached k)` — a
single kernel read did not finish in 900 s. The mechanism is worse than the list walk: the kernel
evaluates `Array.ofFn` as `go` with `acc.push`, and `push` on a kernel array is list append, so the
array is rebuilt quadratically — Θ(n²), ~2.2×10¹⁰ primitive steps per read. Measured at n = 512
(3.2 s) and n = 1024 (16.4 s), the fit is ×4.9 per doubling, i.e. **5×10⁵–3×10⁶ s per read at
n = 209010** (6–37 days) — five to six orders above your figure. (Your `kTab` function form, which the spot checks
actually use, is a different and much cheaper path; the 0.1 s sentence is about the array.)

The consequence for any project that wants to kernel-check the search — and I believe this will come
up, because `basicF_sound` makes it possible in principle — is that a fast accessor is not a
convenience but the whole game. The best one I could build is a tree of **named** definitions
(64 × 64 × 52), because the kernel copies a definition's value term when it unfolds it: a flat
209010-node literal costs ~12 MB per read, while a tree of named 64-entry segments costs three small
unfolds. That reads at **6.2 ms per read** on my machine — a factor ~10⁸ better than the shipped
shape, and still 6 000× above 1 µs.

## 2. The read count in the cover is not 56 per leaf

`basicF` reads the whole distance span of each pair, i.e. gap `r` is read `(r+1)(6−r)` times per box,
so a box costs `Σ_r (r+1)(6−r)·w_r` reads. Instrumenting your `verifier/verify.cpp` (its counts on
the stock build reproduce `certificate/cpp_verification.json` exactly: 60 467 309 nodes,
30 233 655 leaves, 21 157 274 basic, 9 076 381 affine) gives the exact figure over your own accepted
basic-test boxes: **1 142 293 396 938 reads** in total, min 15 190 / median 36 270 reads per box.
Your search never accepts a narrow box — the minimum maximum-width is 490 — precisely because the
affine test exists to settle boxes of width ≤ 512.

At the measured 6.2 ms per read that is **~224 years** for the basic-test half of Axiom 1 (10.9
years if a quiet machine is 20× faster; ~13 days even at the 1 µs/read I had hoped for). So a full
kernel replay of Axiom 1 remains out of reach, and Axioms 2 and 3 are worse (28 pairs, 262 145-entry
table, 267 M / 286 M accepted boxes). This is not a criticism of your proof; it is the number that
tells us what the trust reduction would cost.

## 3. What the kernel *can* check here, and the second wall (memory)

Two things are true at once, and I would rather state both than oversell.

**What checked.** Your four spot boxes, re-proved through the new accessor —
`cert/Spot.lean`: `spot_lattice`, `spot_double`, `spot_corner`, `spot_vacancy`, each
`basicF kT … = true` by `decide +kernel`, about 1.5 s of CPU each (224 table reads per box). That is
also the fidelity check on my side: the table and the checker arithmetic agree with yours on your own
ground truth.

**What did not check, and why.** I generated the certificate for accepted boxes of your search
(taken from your verifier, ranked by volume per read) but could not get a single accepted box through
the kernel on my machine: **`decide +kernel` retains the reduction terms of every table read**, at
~0.4 MB per read. The cheapest box in your cover (`[245,246,245,245,245,490]`, 15 200 reads) peaked
at **6.3 GB RSS** and was killed at 61 s; the 27 452-read class needs 7 GB. So the practical unit of a
kernel-checked cover is **one accepted box per ~6 GB of RAM**, and every box costs at least 15 190
reads. That is a new wall, invisible in the read-count arithmetic and not removed by a faster
accessor (the retention is per unfold).

If the certificate is of interest, `cert/Partial.lean` is generated and type-checked, with one
theorem per covered box so a machine with more headroom can check them one at a time; I would be glad
to run it on a bigger host and send the result rather than assert it.

## 4. What might actually help you

1. **A correction to the Spot.lean comment.** "each costing the kernel about 0.1 s" is measured at
   5×10⁵–3×10⁶ s for the `kTabArray` shape, for the reason in §1 (`Array.ofFn` ⇒ quadratic `push`). If you
   ever want the kernel to touch the table, the honest note is that the array shape, not the kernel's
   list representation alone, is what makes it hopeless.
2. **The named-definition accessor**, if you ever want kernel-checked samples at scale: it makes a
   single `basicF` box (width ~500) cost ~2.5 minutes instead of years, which is enough for
   sampling-based smoke tests well beyond four boxes.
3. **A `TableSound` bridge** is still the open item: `basicF_sound` needs `TableSound f` for the
   accessor, so a kernel-checked certificate chain needs the one extensional lemma
   `∀ k < 209010, kT k = kTabArray[k]` — 209 010 kernel evaluations of `kTab`, which is a separate
   (and by §1, expensive) computation that I did not attempt.

I would be glad to hand over anything here under whatever licence you prefer — the certificate and
generators are derivative of your Apache-2.0 files and carry your notice. The instrumentation of
your verifier (`tools/patch_dump.py`) is a 20-line addition that reports accepted boxes; the table
accessor generator is `tools/gen_table.py`.

With respect for the result — the local inequality, the ceilings, and the honest way your paper
labels the one computation it does not check.

— [author], independent; nothing here is affiliated with you or with Anthropic, and nothing has been
posted publicly.

---

## Notes for whoever sends this (internal)

* Not posted, not emailed. Needs the author's address and a decision about attaching files.
* Tone check: the author explicitly asks the reader to trust the compiler for exactly one
  computation; the note must not read as an accusation of a gap. It is a cost measurement plus a
  pilot certificate.
* Before sending: re-verify `cert/Spot.lean` and `cert/Partial.lean` on a quiet machine and paste the
  wall-clock times, and re-check that the counts in §2 still match `cpp_verification.json` on a fresh
  checkout.
* Do not send the 1.4 GB box dump; send `tools/patch_dump.py` and the selection JSON instead.
