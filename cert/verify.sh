#!/bin/sh
# Rebuild and re-check the whole Lean side of this repo (core Lean only; no Mathlib, no zeta23).
#   usage: ./cert/verify.sh      (from the repo root; needs Lean 4.33.0-rc2, see lean-toolchain)
set -eu
cd "$(dirname "$0")/.."
TOOLCHAIN=$(cat lean-toolchain)
echo "toolchain: $TOOLCHAIN"
echo "--- 1. his checker arithmetic (verbatim copy) ---"
lean cert/Defs.lean
echo "--- 2. the table accessor (209010 entries from certificate/kernel_lower.bin) ---"
python3 tools/gen_table.py                       # regenerates cert/Table.lean, hash-checked
lean -o cert/Table.olean cert/Table.lean
lean -o cert/Defs.olean cert/Defs.lean
echo "--- 3. his four spot boxes, through our accessor (fidelity check) ---"
LEAN_PATH=cert lean cert/Spot.lean
echo "--- 4. the partial certificate ---"
LEAN_PATH=cert lean cert/Partial.lean
echo "OK: everything kernel-checked"
