# knausgard-cert — measured kernel cost + an Axiom-1 partial-coverage certificate

Independent work on the three computation-axioms of Kristian Muri Knausgård's *"More than 83.9% of
the zeros of the Riemann zeta function are distinct and more than 67.35% are simple and on the
critical line"* (arXiv:2610.08965, repo `github.com/kristianmk/839`, upstream commit
`b280d51bef5ab32b3280b0955d040085ed522d59`). His proof stands; this repo asks only what it costs the
**Lean kernel** to replace one of his three trusted booleans with a checked certificate.

Companion to `../knausgard-audit/` (read that first: `AXIOM_MAP.md`, `CERT_DESIGN.md`).

## Read in this order

| file | what it is |
|---|---|
| `BENCHMARK.md` | **the pivotal measurement**: seconds per kernel table read, per representation; the read-count model for his own accepted boxes; what a full replay really costs |
| `COVERAGE.md` | the honest coverage accounting of the partial certificate, with a coverage-vs-budget curve |
| `cert/` | the self-contained Lean development (core Lean only, no Mathlib, no zeta23): his checker arithmetic (`Defs.lean`), the table as a kernel-cheap accessor (`Table.lean`), his four spot boxes re-checked (`Spot.lean`), the certificate (`Partial.lean`) |
| `DELIVERY_DRAFT.md` | the note to `kristianmk/839` — **draft, not posted** |
| `tools/`, `bench/`, `cert/*.json`, `cert/replay_cost.txt` | generators, benchmark probes, measurements, selection data |

## Headline numbers

- **Per kernel read of his table, shipped shape (`Array.ofFn`): >900 s** (killed); fitted Θ(n²) from
  n=512 (3.2 s) and n=1024 (16.4 s) ⇒ **5×10⁵–3×10⁶ s (6–37 days) per read** at n=209010. The paper's "about 0.1 s" is an
  underestimate by ~6 orders for kernel reads, because a kernel read rebuilds the array with
  list-append `push`.
- **Per kernel read with a tree of named definitions: 6.2 ms** (measured in the certificate
  context; 1.8 ms for a one-unfold accessor). The 10⁵ factor the audit hoped for is real *as a
  ratio* (≈10⁸ from the shipped shape) but the absolute floor is milliseconds, not microseconds.
- **Reads per accepted box: min 15,190, median 36,270** — not the audit's 56 (his search never
  accepts a width-1 box; the affine test exists for width ≤ 512). Whole accepted basic-test cover:
  **1.14×10¹² reads ⇒ 224 years** at 6.2 ms/read, 10.9 years at a 20× faster host.
- **Partial certificate**: 5 of his accepted boxes, **1.26×10⁻¹⁵ of the root box's volume**
  (2.4×10⁻⁷ of the box count) — the honest statement of what a fixed budget buys. Its kernel check did
  not complete on this host: one accepted box needs ~6 GB RSS (`decide +kernel` retains every read's
  reduction terms) and the process is killed at ~6 GB. His four spot boxes *do* kernel-check through
  the new accessor.

## Reproduce

```bash
git clone --depth 1 https://github.com/kristianmk/839 upstream
cd cert && lean Defs.lean && lean Table.lean && LEAN_PATH=. lean Spot.lean
lean -o Defs.olean Defs.lean && lean -o Table.olean Table.lean && lean Partial.lean
```
(`lean` is `v4.33.0-rc2` per `lean-toolchain`; the upstream `verifier/` builds with CMake and is
used, with `tools/patch_dump.py`, as the box generator.)

## Status

Measurement done. Certificate machinery done (his arithmetic + accessor + generator + fidelity
check); the certificate itself is generated but its kernel check is blocked by the measured ~6 GB
memory wall on this host — stated as such in `COVERAGE.md`, not implied otherwise. Nothing posted,
nothing public; the delivery note is a draft only.

---

## Why this repo is up

Public evidence and measurement: what it actually costs the Lean kernel to replace a trusted boolean in the 83.9%-zeros proof with a checked certificate — data for the board's computation-axiom discussion.

[BigO-Hunter](https://github.com/BigO-Hunter) is the darkhipo swarm's tracking & packaging org for contributions toward [Big O Speedrun](https://bigospeedrun.com) — a companion, never the project. Org story: [profile](https://github.com/BigO-Hunter/.github) · [bigo-hunter.github.io](https://bigo-hunter.github.io).

## What work can be done here

Axiom-1 is certified and costed. Open work: certificates for the remaining two trusted booleans; integration with the knausgard-audit findings.

## License

Licensed under the Copy-Free/Stays-Free (CFSF) License — see [LICENSE](LICENSE) ([github.com/darkhipo/cfsf](https://github.com/darkhipo/cfsf)). CFSF: copy-free (use for any purpose) and stays-free (nobody may fence this work). The name is unclaimed in software licensing (checked 2026-11-09) and is deliberately not "Copyfree" — the Copyfree Initiative's certification mark — since CFSF's anti-enclosure condition is excluded by their standard.  Vendored third-party material keeps its upstream license — see [NOTICE](NOTICE.md).
