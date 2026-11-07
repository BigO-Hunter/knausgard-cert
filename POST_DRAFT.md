# POST_DRAFT — courtesy note to Kristian Muri Knausgård's repository

**DRAFT ONLY — NOT POSTED.** Intended channel: an issue (or, if welcomed, a PR) on
`github.com/kristianmk/839`. This is a courtesy note about an external audit of the three
computation-axioms. It claims nothing about the bound and disputes nothing.

---

Subject: closing the three `native_decide` notches — audit of the computation axioms

Hello,

I have read arXiv:2610.08965 and gone through `lean/` and the certificate directories closely,
including `lean/README.md`, `Distinct839/Local/{Checker,Spot,Soundness,RunAll,SpotChecks}.lean`
and the two other `Local/` developments. I am writing because I think the trust notch your §8
documents can be closed with machinery your development already contains, and I would rather do
that with you than around you.

What I found, in your own words: the three axioms record one evaluation each —
`checkAll kTabArray = true` (Distinct839, Line889) and `checkAllPar kTabArray 32 96 = true`
(Simple673) — and everything else (table soundness `kTabArray_sound`, search soundness
`localInequality_of_check` / `_of_checkPar` / `_of_chunks`, the implications to the six theorems)
is standard-axioms-only. Your `Spot.lean` then gives the piece I want to build on:
`basicF_sound : TableSound f → basicF f lo hi = true → BoxOK lo hi`, **general in the box**,
with `basicF` small enough for the kernel (`decide +kernel` in `SpotChecks.lean`). That looks to
me like the certificate-consumer theorem already being in place.

What I measured rather than assumed is the cost side. From your comment in `Spot.lean` — 209010
entries at about 0.1 s each, kernel arrays as lists — and 56 (n=7) / 84 (n=8) table reads per
accepted leaf at your accepted-leaf counts, replaying the covers as they stand is on the order of
a few years (Distinct839) to some decades (Simple673) of kernel time. So I do not think a leaf
cover can be kernel-checked directly, and I am not proposing to try.

What I would like to check with you before spending months on it: whether the bottleneck is the
kernel's *accessor*, not the enumeration. If a table representation with cheap indexing
(segmented literals / index-keyed tree) gets a read to microseconds, the same leaves land at
tens of minutes to a few hours, and the soundness lemmas would be untouched — `basicF` is
parametric in `f : ℕ → ℕ`, and all that is needed on the new accessor is `TableSound`, derivable
from your `kTabArray_sound` by an extensional lemma. My open questions:

1. Was the 0.1 s/entry measured through `kTab` as a function (list walk), or over the `Array`?
   That single number decides whether this is weeks or years of work.
2. Would you accept a `Certificate/` addition (generated leaf arrays + a glue lemma
   `Covers → (∀ leaves, BoxOK) → LocalInequality`) under the licence you already use, on the
   understanding that it changes no constant, no window, no statement?
3. Is there any reason you know of that a re-tuned cover — your leaves merged where the test
   re-passes at the parent — would be unsound in your formalisation? I read `checkAll` as a
   decision procedure with no certificate input, so a certificate path is a new entry point over
   `basicF`, not a retargeting of `checkAll`; corrections welcome.

To be explicit about credit and scope: your proof stands exactly as it is. This is verification of
your verification — replacing one compiled evaluation with kernel-checked enumeration of leaves
you already accept, at your constants, with your tables. You built the hard 90%; the ceiling
theorems and the window work are untouched by anything I would add. If this turns into something
publishable, it is an audit note and a contribution to your repository, not a competing bound,
and I will not post it anywhere before you have seen it. I have posted nothing so far.

If you would rather this not proceed, tell me and it stops.

With thanks for a paper that documents its own trust boundary precisely enough to be audited —
that is rarer than it should be.

---

## Internal notes (not part of the note)

- Do not promise a riemann.fail upload: one ≤2 MB file, pinned unpatched zeta23, and his 14-file
  `upstream_relax.patch` is required (CERT_DESIGN §7). If asked, say so.
- Do not claim the constants can be improved. The audit's only claim is a smaller axiom list.
- If he answers question 1 with "through the `Array`", rerun the estimate before any commitment.
- Offer the partial coverage certificate as the first deliverable: it needs none of his
  cooperation to be useful, and it makes the offer concrete rather than a proposal.
