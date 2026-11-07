# AUDIT_REPORT — Knausgård arXiv:2610.08965 axiom audit

Date 2026-11-07. Scope: the three computation-axioms of the Lean 4 proof-of-record in
`github.com/kristianmk/839` (`lean/`), i.e. the only places where the kernel does not check a
computation. Everything below is read from the paper text and from the repository sources
(fetched copies in `evidence/`); no Lean build was run in this audit.

## Verdict

**All three axioms are kernel-checkable in principle, and the consumer theorem is already in his
repository. None of the three is currently kernel-checkable in practice, and the reason is not
mathematics — it is the cost of reading his kernel table inside Lean's kernel (0.1 s per entry;
5–71 years of kernel time for his leaf counts).** The audit therefore lands on a measurement and
a representation change, not on a new theorem. Effort for all three: 4–7 months, not weeks.

## Findings

1. **The axioms are three `native_decide` booleans, and they are named precisely.**
   `Distinct839|Simple673|Line889.Local.check_passes._native.native_decide.ax_1_1`, recording
   `checkAll kTabArray = true` (runs 1 and 3) and `checkAllPar kTabArray 32 96 = true` (run 2).
   Root boxes `[13926, 209009]⁶`, `[13926, 262143]⁷`, `[13926, 262143]⁶`; tables
   209,010 / 262,144 / 262,144; boxes visited/accepted 60,467,309/30,233,655,
   535,332,163/267,666,082, 572,959,453/286,479,727. Axiom 2 carries **κ\* = 1669159/2478195 =
   0.6735382**, the frontier number.

2. **The trust surface is exactly what the author says it is, and he documents it to the
   sentence.** Table soundness (`kTabArray_sound`), search soundness
   (`localInequality_of_check`, `…_of_checkPar`, `…_of_chunks` — the last general in `depth` and
   in the number of parts), the implications to the six headline theorems, and all six ceiling
   theorems are standard-axioms-only. Nothing else is trusted. `#print axioms` per theorem lists
   exactly the three standard axioms plus one computation axiom.

3. **A kernel-checkable per-box certificate already exists in his tree.**
   `basicF_sound : TableSound f → basicF f lo hi = true → BoxOK lo hi`, for an arbitrary box, with
   `basicF` evaluated by `decide +kernel` in his own twelve spot checks. This is the receipts
   pattern, already built; the certificate design is "cover + one kernel decide per leaf".

4. **The wall is cost, and it is quantified in his own comment** ("the table has 209010 entries,
   each costing the kernel about 0.1 s, and kernel arrays are lists"). At 56–84 table reads per
   accepted leaf and 3.0e7 / 2.7e8 / 2.9e8 leaves, direct kernel replay is ≈5.4 / ≈71 / ≈51 years
   of kernel time. Leaf-count reduction cannot close a gap of that size; **kernel table-access
   cost can**, by ~10^5, which brings the same certificates to ~28 min / ~6.3 h / ~4.4 h.

5. **Consequences for the plan.** (a) Do not promise an axiom-free κ\* in weeks. (b) Do the
   one-day measurement of real kernel read cost first; it gates everything. (c) A partial
   coverage certificate — kernel-check as much of the root box as a fixed budget allows, and
   report the covered fraction — is a real, honest trust reduction available now, with no new
   accessor work, and it de-risks the full run.

6. **Venue: a riemann.fail upload of his proof is blocked, twice over.** The site accepts one
   ≤2 MB Lean file, exact statement match against unmodified pinned `zeta-23-lean`, Lean + nanoda
   replay, 3 uploads/day. His proof needs a 14-file relaxation patch to that dependency, and its
   certificate cannot be inlined in 2 MB. The right channel is his repository plus an audit note.

## Corrections to a first-pass reading (recorded so they are not repeated)

- `localInequality_of_check/_checkPar/_chunks` are about **his** recursion (`searchBox`,
  `checkChunk`), not about an arbitrary leaf list; a certificate version needs a **glue lemma**
  (bisection induction, ~100–200 lines). "Reuse the soundness theorem verbatim for a leaf list"
  is wrong as stated.
- Axiom 2's search is chunked at `depth = 32`, `parts = 96`; the soundness theorem is general in
  both, so a replacement may choose its own division — that part *is* free.
- `checkAll kTabArray` is a **decision procedure, not a certificate checker**: there is no
  argument through which a different cover could be fed to it. Any certificate path is a new
  checker entry point (thin wrapper over `basicF`), not a retargeted `checkAll`.
- Effort: 4–8 weeks was too optimistic by roughly 3–4×; see CERT_DESIGN §6.

## Recommended first certificate

**Axiom 1 (Distinct839, Proposition 3.3), as a partial coverage certificate**: his table and his
`basicF_sound`, a kernel-checked cover of the fraction of the root box that fits a fixed kernel
budget (start at 10^6 reads), honest coverage accounting, and the generator validated against his
four spot boxes and his accepted/visited counters. It is the smallest of the three (n=7, 209,010
table), it exercises exactly the machinery axioms 2 and 3 need, and it yields a measured
reduction of the trusted surface rather than a promise. Then κ\* (axiom 2).

## Not checked (stated plainly)

- No Lean build, no certificate generation, no timing was run here. The 0.1 s/entry figure is the
  author's; the 5–71 year projections follow from it arithmetically.
- Whether a kernel-cheap table representation really reaches ~1e-6 s/read is **unmeasured** — it
  is the pivotal experiment, not a result.
- The exact 2 MB / statement-match interaction between his patched statements and the site's
  pinned `ChallengeDeps` was read from the site's published contract, not exercised.
- All three root boxes and box counts are verbatim from the three `Local/RunAll.lean` docstrings
  (`[13926, 209009]⁶`, `[13926, 262143]⁷`, `[13926, 262143]⁶`); copies in `evidence/`.
- Nothing in this audit disputes his bound, his constants, his statements, or his honesty: the
  trust notch is disclosed, measured and supported by three independent checks. The audit's claim
  is only that the notch can be closed, and at what price.
