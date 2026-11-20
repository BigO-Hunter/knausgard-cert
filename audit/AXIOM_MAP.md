# AXIOM_MAP — the 3 computation-axioms of Knausgård arXiv:2610.08965

Evidence: paper §8 (text at `knausgard.txt`), repo `github.com/kristianmk/839` —
`lean/README.md` ("Axioms"), `lean/*/Local/RunAll.lean`, `lean/*/Local/SpotChecks.lean`,
`lean/Distinct839/Local/{Soundness,Spot,Checker}.lean` (all fetched, see `evidence/`).
Paper title per repo README: "More than 83.9% … distinct and more than 67.35% … simple and
on the critical line".

## What the axioms literally are

Each is one auto-generated `native_decide` axiom, named
`<Dev>.Local.check_passes._native.native_decide.ax_1_1`, recording the truth of the theorem
`check_passes` in `<Dev>/Local/RunAll.lean`. Verbatim (`lean/README.md`, "Axioms"):

> "Each of the three extra axioms is recorded by `native_decide` for one evaluation: the
> statement `checkAll kTabArray = true` of `Distinct839/Local/RunAll.lean` and of
> `Line889/Local/RunAll.lean`, and the statement `checkAllPar kTabArray 32 96 = true` of
> `Simple673/Local/RunAll.lean`. The table is evaluated by Lean's interpreter and the checker
> by compiled code. … This trusts the Lean compiler, interpreter and runtime for these three
> computations."

Paper §8, verbatim:

> "What Lean's kernel does not check is one evaluation, the statement that the search returns
> true on the table. It is carried out by the tactic native_decide: the table is evaluated by
> Lean's interpreter and the search by compiled code, and the outcome is recorded as an axiom.
> This trusts the Lean compiler, interpreter and runtime for this one computation."

So each axiom is a **single boolean**: a deterministic branch-and-bound function, applied to a
frozen table, returned `true` on the whole root box.

## The three axioms

| # | Dev / file | Statement | Root box (grid units, H=16384) | Table | Boxes visited / accepted |
|---|---|---|---|---|---|
| 1 | `Distinct839/Local/RunAll.lean` | `checkAll kTabArray = true` | `[13926, 209009]⁶` (6 gaps, 7 pts) | 209,010 | 60,467,309 / 30,233,655 |
| 2 | `Simple673/Local/RunAll.lean` | `checkAllPar kTabArray 32 96 = true` | `[13926, 262143]⁷` (7 gaps, 8 pts) | 262,144 | 535,332,163 / 267,666,082 |
| 3 | `Line889/Local/RunAll.lean` | `checkAll kTabArray = true` | `[13926, 262143]⁶` | 262,144 | 572,959,453 / 286,479,727 |

Consumers (paper Table 5/6, verbatim mapping): axiom 1 → Theorem 1.1 + Corollary 1.2 +
second bound of Thm 1.4; axiom 2 → Theorem 1.3 + first bound of Thm 1.4; axiom 3 → Thm 1.5.

Headline numbers (verified verbatim in §8):
`distinct_zeros_839` 1645064/1960733 = 0.8390046 · `simple_zeros_678` 1329395/1960733 =
0.6780092 · **`simple_critical_zeros_673` 1669159/2478195 = 0.6735382 (κ\*, the frontier)** ·
`average_simple_and_critical_8367` 2073677/2478195 · `simple_or_critical_8891` 3376433/3797325 ·
`simple_or_critical_8893` 50652159/56956375 = 0.8893150.

## What each search asserts, mathematically

One inequality per leaf, over a box of gap vectors; all four stages are decidable integer tests
(`Checker.lean`, `node`), evaluated in `Nat` with signed pairs (`SInt`):

1. **stage 0** pressure test (box wide ⇒ accept by pressure alone);
2. **stage 1** range-minimum test (`basicF`): kernel-table cell minima + piecewise-linear
   potential minima + label-raising penalty;
3. **stage 2** affine-support test (`affineOK`), only for boxes of width ≤ 512: all-simple
   labelling plus penalty, else all 128 labellings one at a time;
4. else split the widest gap at its midpoint (`.split`), recursing to width 1, where
   `Verdict.fail` is possible in principle.

`checkAll` = `searchPath (node tab (sparse tab)) cFuel … rootLo rootHi`; `checkAllPar tab depth
parts` = the same search cut after `depth` splits into `parts` chunks (`checkChunk`), joined by
`localInequality_of_checkPar : … ∀ depth parts, parts ≥ 1, checkAllPar tab depth parts = true →
LocalInequality` (kernel-checked, standard axioms).

## What is already kernel-checked (standard axioms only)

Per `lean/README.md` and `Soundness.lean`:

- `kTabArray_sound` / `kTab_sound` — the table is a sound lower bound for `K(t)²` on each cell.
- `localInequality_of_check`, `localInequality_of_checkPar`, `localInequality_of_chunks` — the
  **search soundness**: accepted root box ⇒ `LocalInequality`. Not merely for the fixed run:
  `localInequality_of_chunks` quantifies over *arbitrary* `depth` and `n` (`0 < n`).
- `basicF_sound : TableSound f → basicF f lo hi = true → BoxOK lo hi` — **the
  certificate-consumer theorem already exists, for an arbitrary box**, and `basicF` is
  kernel-evaluable (`by decide +kernel`, used for all 12 spot boxes).
- The implications `LocalInequality →` the six headline theorems (`…_of_local`), and the six
  ceiling theorems (no computation at all).

## Classification

Per-axiom, three labels: KERNEL-CHECKABLE-CERTIFICATE (a witness + per-item decidable check
discharges it), NEEDS-VERIFIED-SEARCH (as shipped: one trusted compiled boolean),
ANALYTIC (needs a new certified inequality rather than enumeration).

| Axiom | As shipped | Consumer theorem exists? | Classification |
|---|---|---|---|
| 1 Distinct839 | 1 trusted boolean | **yes** (`basicF_sound`) | NEEDS-VERIFIED-SEARCH → KERNEL-CHECKABLE-CERTIFICATE, **blocked on kernel table-access cost** (CERT_DESIGN §2) |
| 2 Simple673 (**κ\***) | 1 trusted boolean (chunked, 96 parts) | **yes** (`basicF_sound` + `localInequality_of_chunks`/`_checkPar`) | same |
| 3 Line889 | 1 trusted boolean | **yes** | same |

None of the three is ANALYTIC *as stated* — the per-leaf test is a decidable integer
comparison and the soundness implications are already theorems. What is missing is not a
theorem but a **feasible certificate size**, and that is an engineering fact about Lean's
kernel, not about his mathematics. See CERT_DESIGN.md for the arithmetic that makes this the
central finding of the audit.

## What the author gives us for free

1. The certificate-consumer theorem (`basicF_sound`), general in the box.
2. Table soundness `kTabArray_sound` (exact rational arithmetic, kernel-checked).
3. Search soundness in three interface shapes, including chunk-depth-general.
4. Kernel-evaluated ground truth: 12 spot boxes (`SpotChecks.lean`, `decide +kernel`), one per
   run at the numerically-found minimum-slack point (≈1.3e-5 for run 2; ≈1.0e-5 and 2.0e-5 for
   run 3).
5. Cross-checks: table identical to the reference `kernel_lower.bin` in every entry; counter
   drivers reproducing the C++/Python box counts exactly; `CHECKSUMS.sha256`.
6. Precedent he himself names for kernel-checked enumeration: 5,651 cases [26 = Lavery],
   ~1,500 generated files [12 = D'Souza].
