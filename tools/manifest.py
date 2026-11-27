#!/usr/bin/env python3
"""Write cert/MANIFEST.txt: hash-pins for the certificate's data (table, box list, Lean files)."""
import hashlib, json, os, subprocess
from pathlib import Path

PLAY = Path(__file__).resolve().parent.parent
UP = Path(os.environ.get("KNAUSGARD_UPSTREAM", str(PLAY / "upstream")))
CERT = PLAY / "cert"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


sel = json.loads((CERT / "selection.json").read_text())
canon = "\n".join(f"{','.join(map(str, b['lo']))} {','.join(map(str, b['hi']))}" for b in sel["chosen"])
lines = [
    "KNAUSGARD AXIOM-1 PARTIAL-CERTIFICATE MANIFEST",
    "upstream            github.com/kristianmk/839 @ b280d51bef5ab32b3280b0955d040085ed522d59",
    f"table               upstream/certificate/kernel_lower.bin  entries={209010}  sha256={sha(UP/'certificate/kernel_lower.bin')}",
    f"table in inputs.json                                       sha256=b80e5a8c70e4beb3b872dada426016bc97b0954c1a8a5eabaeb40fba49cded36",
    f"box list (canonical text, {len(sel['chosen'])} boxes, 'lo hi' per line)  sha256={hashlib.sha256((canon + chr(10)).encode()).hexdigest()}",
    f"selection.json                                         sha256={sha(CERT/'selection.json')}",
    f"cert/Table.lean                                        sha256={sha(CERT/'Table.lean')}",
    f"cert/Defs.lean                                         sha256={sha(CERT/'Defs.lean')}",
    f"cert/Spot.lean                                         sha256={sha(CERT/'Spot.lean')}",
    f"cert/Partial.lean                                      sha256={sha(CERT/'Partial.lean')}",
    f"PARTIAL_CERT.lean (= cert/Partial.lean)                sha256={sha(PLAY/'PARTIAL_CERT.lean') if (PLAY/'PARTIAL_CERT.lean').exists() else 'missing'}",
    "",
    f"boxes               {sel['boxes']} of {sel['pool_size']} accepted basic-test boxes ({sel['covered_box_fraction']:.3e})",
    f"budget reads        {sel['used_reads']} (cap {sel['cap_reads_per_box']} per box)",
    f"covered volume      {sel['covered_volume']} of {sel['root_volume']} = {sel['covered_fraction']:.6e}",
    "",
    "covered boxes (lo | hi, gaps in units of 1/16384):",
]
for b in sel["chosen"]:
    lines.append(f"  {' '.join(map(str, b['lo']))} | {' '.join(map(str, b['hi']))}   (reads {b['reads']})")
(CERT / "MANIFEST.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
