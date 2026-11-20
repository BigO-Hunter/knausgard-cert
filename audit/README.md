# knausgard-audit — audit of the 3 computation-axioms of arXiv:2610.08965

Read in this order: `AUDIT_REPORT.md` (verdict, findings, what was not checked) →
`AXIOM_MAP.md` (the three axioms verbatim, with exact names and consumers) →
`CERT_DESIGN.md` (certificate shape, the cost wall with arithmetic, effort) →
`POST_DRAFT.md` (courtesy note to the author's repo — **not posted**).

Sources: paper text `knausgard.txt`; repository sources in `evidence/` (fetched 2026-11-07 from
`github.com/kristianmk/839` — `lean/README.md`, the three `Local/RunAll.lean`, `Distinct839/Local/
{Checker,Spot,Soundness}.lean`, `SpotChecks.lean`); riemann.fail submission contract in
`evidence/riemann_CONTRIBUTING.md`.

## One-paragraph summary

All three axioms are single trusted booleans — a compiled `native_decide` run of a deterministic
branch-and-bound — behind an otherwise fully kernel-checked development. His tree already
contains the certificate-consumer theorem (`basicF_sound`, general in the box, `basicF`
kernel-evaluable), so the pattern is not speculative. What stands in the way is measured cost:
0.1 s per kernel table read, ~56–84 reads per accepted leaf, 3.0e7 / 2.7e8 / 2.9e8 leaves ⇒
≈5.4 / ≈71 / ≈51 years of kernel time. Leaf-count reduction cannot close that; a ~10^5× kernel
table-access cost reduction can (⇒ ~28 min / ~6.3 h / ~4.4 h). Recommended first artifact: a
**partial coverage certificate** for Axiom 1 with honest coverage accounting, after a one-day
measurement of real kernel read cost. All three: 4–7 months. riemann.fail is not the channel
(2 MB one-file cap, unpatched pinned zeta23, his 14-file dependency patch required).

Status: DRAFTS. Nothing posted, nothing public, no build run. HOME-durable workdir.
