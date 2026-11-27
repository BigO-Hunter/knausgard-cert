#!/bin/sh
# Rebuild and re-check the Lean side of this repo (core Lean only; no Mathlib, no zeta23).
#   usage: ./cert/verify.sh          fidelity check: Defs + Table + his four spot boxes
#          ./cert/verify.sh --full   also attempt the 5-box partial certificate (needs ~7 GB RAM
#                                    per box; see COVERAGE.md "Status of the kernel check")
# Needs Lean v4.33.0-rc2 (pinned in lean-toolchain; elan installs it automatically).
set -eu
cd "$(dirname "$0")/.."
TOOLCHAIN=$(cat lean-toolchain)
echo "toolchain: $TOOLCHAIN"
echo "--- 1. his checker arithmetic (verbatim copy) ---"
lean -o cert/Defs.olean cert/Defs.lean
echo "--- 2. the table accessor (209010 entries) ---"
if [ -d upstream/certificate ]; then
    python3 tools/gen_table.py                   # regenerate cert/Table.lean, hash-checked
else
    echo "upstream/ absent: using the committed cert/Table.lean (sha256-pinned in cert/MANIFEST.txt)"
fi
lean -o cert/Table.olean cert/Table.lean
echo "--- 3. his four spot boxes, through our accessor (fidelity check) ---"
LEAN_PATH=cert lean cert/Spot.lean
echo "OK: spot boxes kernel-checked"
if [ "${1:-}" = "--full" ]; then
    echo "--- 4. the partial certificate (memory wall: ~6-7 GB RSS per box, may be killed) ---"
    LEAN_PATH=cert lean cert/Partial.lean
    echo "OK: partial certificate kernel-checked"
fi
