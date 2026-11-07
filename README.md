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
- **Partial certificate**: 5 of his accepted boxes, kernel-checked, **1.4×10⁻¹⁴ of the root box's
  volume** (9×10⁻⁷ of the box count) — the honest statement of what a fixed budget buys.

## Reproduce

```bash
git clone --depth 1 https://github.com/kristianmk/839 upstream
cd cert && lean Defs.lean && lean Table.lean && LEAN_PATH=. lean Spot.lean
lean -o Defs.olean Defs.lean && lean -o Table.olean Table.lean && lean Partial.lean
```
(`lean` is `v4.33.0-rc2` per `lean-toolchain`; the upstream `verifier/` builds with CMake and is
used, with `tools/patch_dump.py`, as the box generator.)

## Status

Measurement done; certificate pilot done; nothing posted, nothing public; delivery note drafted only.
