-- Cert/Spot.lean
-- FIDELITY CHECK: the four boxes of the author's own kernel-checked spot checks
-- (Distinct839/Local/SpotChecks.lean, upstream commit b280d51b), re-run here through OUR table
-- accessor Cert.kT. His four theorems are `basicF_sound kTab kTab_sound _ _ (by decide +kernel)`;
-- the same four boxes must return `true` from `basicF Cert.kT`, which is only possible if
--   (a) our reimplementation of basicF is his (it is a verbatim copy, see Cert/Defs.lean), and
--   (b) our table agrees with his kTab entry for entry on the cells the four boxes read.
-- If these four theorems check, the generator and the accessor are validated on his ground truth.
import Defs
import Table

namespace Cert

open Distinct839.Local

theorem spot_lattice : basicF kT #[16790, 16790, 16790, 16790, 16790, 16790]
    #[16794, 16794, 16794, 16794, 16794, 16794] = true := by decide +kernel

theorem spot_double : basicF kT #[31900, 31900, 31900, 31900, 31900, 31900]
    #[31904, 31904, 31904, 31904, 31904, 31904] = true := by decide +kernel

theorem spot_corner : basicF kT #[13926, 13926, 13926, 13926, 13926, 13926]
    #[13930, 13930, 13930, 13930, 13930, 13930] = true := by decide +kernel

theorem spot_vacancy : basicF kT #[17039, 16733, 16723, 16733, 17039, 30419]
    #[17043, 16737, 16727, 16737, 17043, 30423] = true := by decide +kernel

end Cert
