# mānadaṇḍa across the DCS corpus — census

_Created: 2026-10-06 · Last updated: 2026-10-06_

Corpus pin: DCS CoNLL-U flatten `dcs_full.sqlite` (gasyoun/dcs-conllu @
`04e0778d`, imported 2026-10-03; 270 texts, 5,688,416 tokens; IAST surface).
Eval code: [`scripts/manadanda_census.py`](../scripts/manadanda_census.py)
(`--selftest` included; re-run after any corpus re-pin). Data:
[`manadanda_census.csv`](../observatory/site/src/data/manadanda_census.csv),
[`manadanda_danda_family.csv`](../observatory/site/src/data/manadanda_danda_family.csv).

## 1. Question

Kumārasaṃbhava 1.1 makes the Himalayas *sthitaḥ pṛthivyā iva mānadaṇḍaḥ*
— "standing like the measuring-rod of the earth". How often does this
compound actually occur in the full machine-readable DCS corpus, in what
periods and registers, and does anything beyond the Kālidāsa verse reuse it?

## 2. Method

Token-level, sandhi-safe: a **mānadaṇḍa** attestation is a token with lemma
`daṇḍ…`, `feat_case ≠ Cpd` (inflected final member), immediately preceded by
a `Cpd` member with lemma `māna`; the member run is walked back to reconstruct
the full compound. An independent substring scan of the sandhied sentence text
(`mānadaṇḍ`) must agree sent_id-for-sent_id (selftest enforces this). Time
slots from DCS `chapter-info.xml` (dcsTimeSlot 1–5), era labels per the
VisualDCS Fonetika slot_era_map. The **context family** is every
compound-final `daṇḍa` token under the same rule (any first members);
sandhi-fused plain *daṇḍa* (e.g. *tasmāt + daṇḍaḥ* → surface *tasmāddaṇḍaḥ*)
is excluded by construction.

## 3. Result: exactly two attestations

| # | Text | Loc. | Compound (members) | Morph | Slot / era |
|---|------|------|--------------------|-------|------------|
| 1 | Kumārasaṃbhava | 1.1 (pādas cd), DCS `KumSaṃ, 1` sent 485110 | māna+daṇḍa | Nom Sg Masc | 3 — Early classical (~200–600 CE) |
| 2 | Kāvyālaṃkāra (Bhāmaha) | **3.36** pādas ab, DCS `KāvyAl, 3` sent 364306 | samagra+gagana+āyāma+māna+daṇḍa | Nom Sg Masc | 3 — Early classical |

Frequencies: 2 / 5,688,416 tokens = **0.35 per million tokens** (2 / 4,240,775
surface words = 0.47 per million words). Lemma *daṇḍa* overall: 2,046 tokens.
Zero attestations in slots 1–2 (Vedic, Epic): the compound first surfaces in
the kāvya register of the early classical period and never leaves it.

Verse 2 in full (DCS text; slot-3 counter maps 1:1 onto GRETIL verse numbers
in this chapter, checked against
[bhakavpu.htm](https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/5_poetry/1_alam/bhakavpu.htm)):

> **samagragaganāyāmamānadaṇḍo rathāṅginaḥ /**
> **pādo jayati siddhasrīmukhendunavadarpaṇaḥ // Bh_3.36 //**

an udāharaṇa for **upamārūpaka** following the kārikā *upamānena tadbhāvam
upameyasya sādhayan / yāṃ vadaty upamāmetad upamārūpakaṃ yathā* (Bh 3.35).
GRETIL's edition reads *siddhastrī-mukha-* (edM) where DCS has
*siddhasrī-mukha-* — a lectionis nota to resolve before any stemmatic claim.

## 4. Context: the compound-final -daṇḍa family

489 tokens, 212 distinct compounds across the corpus. Era profile: Epic &
early śāstra 191 · Early classical 110 · Later classical 82 · Vedic 72 ·
Medieval 34. Top members are non-metaphorical throughout: *sāhasa-daṇḍa*
(legal fine, ×27), *loha-daṇḍa* (iron rod, rasaśāstra, ×23),
*maitrāvaruṇa-daṇḍa* (ritual staff, ×16), *heman-daṇḍa* (gold rod, ×16),
*śrī-daṇḍa* (×13), *dhṛta-daṇḍa* (×12), *srug-daṇḍa* / *prāñc-daṇḍa* (ritual,
×10/×9), *nyasta-daṇḍa* (×10), *rukma-daṇḍa* (×10). The family is dominated by
legal-administrative, ritual and technical rods; **mānadaṇḍa is the only
"rod as measure" metaphor in the family, and it occurs exactly twice — both
times in kāvya-adjacent slot-3 texts.**

## 5. Dictionary coverage (checked 2026-10-06, local snapshots)

*mānadaṇḍa* is absent as a headword from MW (`MW72/20161107/mwiast.txt`),
PWG (`PWG/pwg_ls*`), Apte (`AP90`), and CCS — i.e. the image that opens
Kālidāsa's Kumārasaṃbhava is not in the standard dictionary stock these
snapshots represent.

## 6. Attribution candidate: Bhāmaha 3.36 ← Kumārasaṃbhava 1.1

Evidence for direct reuse of Kālidāsa by Bhāmaha's example verse:

1. **Rarity.** Corpus-wide the compound is a near-hapax pair; there is no
   pre-Kālidāsa (slot 1–2) antecedent to normalize either occurrence, so the
   shared item cannot be a common cliché the corpus can still see.
2. **Same metaphor frame.** Both verses appose a cosmic entity to a
   measuring-rod of a spatial whole: the Himalaya as *pṛthivyā … mānadaṇḍaḥ*
   (rod of the earth) → the sun as *samagragaganāyāma-mānadaṇḍaḥ* (rod of the
   whole sky's expanse). Domain inversion earth→sky, structure preserved.
3. **Same maṅgala stance.** Kum 1.1 opens the poem as its benedictory
   mountain-verse; Bhāmaha's example is itself a *pādo jayati* blessing — the
   reuse imports the canon's maṅgala posture into the alaṃkāra classroom.
4. **Chronology allows it.** Kālidāsa (late Gupta) predates Bhāmaha by
   consensus (conventionally late 7th–8th c. CE; note DCS slots the text 3,
   ~200–600, against that convention — a DCS assignment worth flagging, not a
   date claim of ours).
5. **Example-verse economy.** Bhāmaha's ch. 2 examples demonstrably circulate
   cross-author (GRETIL marks Bh 2.87 as cited by Daṇḍin, Kāvyādarśa 2.244);
   the alaṃkāra udāharaṇa pool traded in canonical kāvya material.

Counterweights, honestly: a lost common source (pre-Kālidāsa kāvya stock) is
corpus-internally irrefutable since DCS holds no pre-Kālidāsa kāvya; and the
*siddhasrī-/siddhastrī-* variant shows the verse text was still moving.
Verdict: **attribution candidate (probable Kālidāsa→Bhāmaha reuse), not a
proven borrowing** — strong enough to cite as "the compound's only other
attestation", too weak for stemmatic claims without collation.

## 7. Reproduce

```
python scripts/manadanda_census.py --selftest   # asserts the 2-attestation set
python scripts/manadanda_census.py              # rewrites both CSVs (~30 s)
python scripts/data_index.py --check            # catalog gate stays green
```

_Gasūns_
