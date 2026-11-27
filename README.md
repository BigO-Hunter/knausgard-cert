# knausgard-cert — measured kernel cost + an Axiom-1 partial-coverage certificate

Independent work on the three computation-axioms of Kristian Muri Knausgård's *"More than 83.9% of
the zeros of the Riemann zeta function are distinct and more than 67.35% are simple and on the
critical line"* (arXiv:2610.08965, repo `github.com/kristianmk/839`, upstream commit
`b280d51bef5ab32b3280b0955d040085ed522d59`). His proof stands; this repo asks only what it costs the
**Lean kernel** to replace one of his three trusted booleans with a checked certificate.

**Board context.** This is independent verification work, not a [Big O Speedrun](https://bigospeedrun.com)
race entry: it improves no bound. The related *zeta zeros critical line* race is open (leader:
H. M. Bui + 2 more, κ* ≥ 0.703703, Nov 20 2026, Claimed); Knausgård's distinct-zeros result is a
separate target. The findings here — the kernel table-read cost, the memory wall, and the
certificate machinery — apply to any attempt to kernel-check a large compiled computation.

Companion audit: `audit/` (read first: `AXIOM_MAP.md`, `CERT_DESIGN.md`).

## Read in this order

| file | what it is |
|---|---|
| `BENCHMARK.md` | **the pivotal measurement**: seconds per kernel table read, per representation; the read-count model for his own accepted boxes; what a full replay really costs |
| `COVERAGE.md` | the honest coverage accounting of the partial certificate, with a coverage-vs-budget curve |
| `cert/` | the self-contained Lean development (core Lean only, no Mathlib, no zeta23): his checker arithmetic (`Defs.lean`), the table as a kernel-cheap accessor (`Table.lean`), his four spot boxes re-checked (`Spot.lean`), the certificate (`Partial.lean`) |
| `PROVENANCE.md`, `cert/MANIFEST.txt` | upstream pin, verbatim-copy accounting, sha256 pins, kernel-check status |
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
  not complete on the measurement host: one accepted box needs ~6 GB RSS (`decide +kernel` retains every read's
  reduction terms) and the process is killed at ~6 GB. His four spot boxes *do* kernel-check through
  the new accessor.

## Reproduce / verify

```bash
./cert/verify.sh          # Defs + Table + his four spot boxes, kernel-checked
./cert/verify.sh --full   # also attempt the 5-box certificate (~7 GB RAM per box; see COVERAGE.md)
```

Lean `v4.33.0-rc2` is pinned in `lean-toolchain` (elan installs it automatically). CI runs the
fidelity check on every push (`.github/workflows/ci.yml`). To regenerate the table from upstream:
`git clone --depth 1 https://github.com/kristianmk/839 upstream` (see `PROVENANCE.md`), then
`python3 tools/gen_table.py` (sha256-checked against his `inputs.json`). The benchmark reproduction
is in `BENCHMARK.md` §8; the box generator is `tools/patch_dump.py` + his `verifier/`.

## Status

Measurement done. Certificate machinery done (his arithmetic + accessor + generator +
fidelity check); the certificate itself is generated but its kernel check is blocked
by the measured ~6 GB memory wall — stated as such in `COVERAGE.md`.

## Audit lane

`audit/` — the knausgard-audit: the three computation-axioms mapped, classified and costed for the
Knausgård 83.9%-distinct-zeros proof, with the upstream sources it read (`evidence/`). Its
pre-measurement cost projections were corrected by `BENCHMARK.md`; `audit/README.md` says where.

## Next steps for a continuer

- **Run the certificate on a bigger host.** `cert/Partial.lean`'s per-box theorems
  (`covered_0 … covered_4`) are each one line that kernel-checks in ~95 s given ~7 GB of RAM.
- **The `TableSound` bridge**: `∀ k < 209010, kT k = kTabArray[k]` — the extensional lemma that
  connects the accessor to his soundness theorem (`COVERAGE.md`, "What would have to be true").
- **Axioms 2 and 3** (Simple673, Line889): the same machinery, larger tables and more accepted
  boxes (`BENCHMARK.md` §6) — both strictly worse than Axiom 1.
- **Route B**: a certified analytic majorant per box, no table reads (`audit/CERT_DESIGN.md`) —
  the only path to a human-readable case count; the measurements here strengthen that recommendation.
- **Share the measurements upstream** with the author (`kristianmk/839`): the "about 0.1 s per
  entry" comment in his `Spot.lean` is an underestimate by ~6 orders for the array shape, for the
  reason in `BENCHMARK.md` §2.

## License

Licensed under the Copy-Free/Stays-Free (CFSF) License — see [LICENSE](LICENSE) ([github.com/darkhipo/cfsf](https://github.com/darkhipo/cfsf)). CFSF: copy-free (use for any purpose) and stays-free (nobody may fence this work). Vendored third-party material keeps its upstream license — see [NOTICE](NOTICE.md).

Part of [BigO-Hunter](https://github.com/BigO-Hunter) — independent verification and packaging for [Big O Speedrun](https://bigospeedrun.com) · [org profile](https://github.com/BigO-Hunter/.github) · [bigo-hunter.github.io](https://bigo-hunter.github.io).
