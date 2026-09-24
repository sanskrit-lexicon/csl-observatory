# PWG-ls vs CDSL pwgauth — comparison report

_Generated: 24-09-2026 · comparison script `pwg_ls_vs_cdsl_compare.py`, this pass._

## Inputs

- `PWG-ls.txt`: 2735 lines → 2680 distinct non-empty normalized values (0 duplicated values, max repeat 1)
- `pwgbib_input.txt` (CDSL pwgauth): 2844 records → 2838 distinct codes (6 codes appearing on 2+ records)
- Normalization: NFC + whitespace collapse; case PRESERVED (case is meaningful in this bibliography).

## Provenance & interpretation (MG ruling, grill 24-09-2026)

- `PWG-ls.txt` is **Andhrabharati's update to CDSL** (MG: «The .txt file give is what Andhrabharati
  made, it's an update to CDSL»), sha256
  `f44ae1bbccca1ceb508e9da0c1c389dcb93910fb570d0a4d962819cf756b5fd0`.
- So ADDED = abbreviations **new in the Andhrabharati update**, DELETED = abbreviations **present in
  CDSL pwgbib but dropped by Andhrabharati**. No deletion queues are built from this report —
  «No need to delete … No hand queue, do full auto comparison» (MG 24-09-2026).

## Headline numbers (exact match)

- Matched (in both): **2006**
- ADDED candidates (cited as `<ls>` in PWG-ls, NO pwgbib code): **674**
- DELETED candidates (pwgbib code, never appears in PWG-ls): **832**

## Case-only residue

- of the ADDED set, 10 differ from some bib code only by letter case
- of the DELETED set, 19 have a case-variant present in PWG-ls
- true ADDED after case pass: **664** · true DELETED after case pass: **813**

## Prefix attribution (CDSL longest-prefix method)

- ADDED: 449 of 664 extend a known bib code (volume/edition/commentary/qualifier suffixes) — true UNKNOWN residue: **215**
- DELETED: 86 of 813 are prefixes of longer cited ls values (cited in extended form) — totally uncited: **727**

## Duplicates inside each list

- pwgbib_input duplicate codes: 6 — ['Ind. des KANDYUR', 'KANDYUR', 'LIA.', 'SUPADMAVYĀKARAṆA', 'WILSON, Hindu Th.', 'WILSON, Sel. spec. of the Theatre of the Hindus'] …

## Samples

### first 25 ADDED candidates
- `2ten VP.` (×1)
- `4te RĀJA-TAR.` (×1)
- `AGASTYASAṂH.` (×1)
- `AINSL.` (×1)
- `AIT. BR. Comm.` (×1)
- `AIT. ĀRAṆY.` (×1)
- `AIT. ĀRAṆYAKA` (×1)
- `AK. (COLEBR.)` (×1)
- `AK. (LOIS.)` (×1)
- `AK. COL.` (×1)
- `ALAṂKĀRAC. Eing.` (×1)
- `AMṚTAB. UP.` (×1)
- `AMṚTABINDŪP.` (×1)
- `ANANTASAṂHITĀ` (×1)
- `ANUKR. ŚĀṬY. BR.` (×1)
- `AUFR. De accentu comp.` (×1)
- `AUFR. HALĀY. Ind.` (×1)
- `AUFRECHT, HALĀY. Ind.` (×1)
- `AUFRECHT, UṆĀDIS. Ind.` (×1)
- `AUFRECHTʼs Ausg. des HALĀY.` (×1)
- `AVIC.` (×1)
- `Abh. d. Königl. Ak. d. W. zu Berlin` (×1)
- `As. J. new s.` (×1)
- `Asiatischen Museum der Kais. Akad. d. Wiss. in St. Petersburg` (×1)
- `BAER und HELMERSEN, Beitr. z. Kenntn. d. russ. Reiches` (×1)

### first 25 DELETED candidates
- `?`
- `A Gloss. of jud. and rev. terms`
- `A. C. BURNELL`
- `ADHIMĀS.`
- `AGASTYASAṂH`
- `AGAYAPĀLA`
- `AH.`
- `AINSL`
- `AINSLIE, Mat. ind.`
- `AIT.`
- `ALAṂKĀRAC.`
- `ALBY.`
- `ALBYROUNY'S`
- `AMṚTABINDŪP`
- `AMṚTAV. UP.`
- `AMṚTAVINDŪP.`
- `ANANDAL.`
- `ANANTASAM̃HITĀ`
- `ANEKĀRTHAKOŚA`
- `ANUKRAM.`
- `APAG. AV.`
- `AR. UP.`
- `ARHANT'S`
- `ARYABH.`
- `AUFRECHT'S`

### first 25 truly-UNKNOWN added candidates (no bib prefix)
- `2ten VP.` (×1)
- `4te RĀJA-TAR.` (×1)
- `AMṚTAB. UP.` (×1)
- `ANANTASAṂHITĀ` (×1)
- `AVIC.` (×1)
- `Abh. d. Königl. Ak. d. W. zu Berlin` (×1)
- `Asiatischen Museum der Kais. Akad. d. Wiss. in St. Petersburg` (×1)
- `BERGSTEDT` (×1)
- `BIJĀBHIDHĀNA` (×1)
- `BRAHMAYĀMALA` (×1)
- `BUCHANANʼs Handschrr.` (×1)
- `BUCHANANʼs Hdschrr.` (×1)
- `Berichte der phil.-hist. Cl. d. k. s. G. d. Ww.` (×1)
- `Bibl. indica` (×1)
- `Bomb.` (×1)
- `Bomb. Ausg.` (×1)
- `Bomb. Ausgg.` (×1)
- `Bombay 1783 (1861) lithographirten` (×1)
- `Breslauer Programm` (×1)
- `Buddh. Trigl.` (×1)
- `Bull. de lʼAcad. Imp. des Sc.` (×1)
- `Bull. de lʼAcad. Imp. des Sc. de S.-P.` (×1)
- `Bull. de lʼAcad. Imp. des Sc. de St. P.` (×1)
- `Bulletin de lʼAcad. Imp. des sc. de St.-Pét.` (×1)
- `BĪJAGAṆITA` (×1)

### first 25 added that extend a known bib code
- `AGASTYASAṂH.` ← extends `AGASTYASAṂH`
- `AINSL.` ← extends `AINSL`
- `AIT. BR. Comm.` ← extends `AIT. BR.`
- `AIT. ĀRAṆY.` ← extends `AIT.`
- `AIT. ĀRAṆYAKA` ← extends `AIT.`
- `AK. (COLEBR.)` ← extends `AK.`
- `AK. (LOIS.)` ← extends `AK.`
- `AK. COL.` ← extends `AK.`
- `ALAṂKĀRAC. Eing.` ← extends `ALAṂKĀRAC.`
- `AMṚTABINDŪP.` ← extends `AMṚTABINDŪP`
- `ANUKR. ŚĀṬY. BR.` ← extends `ANUKR.`
- `AUFR. De accentu comp.` ← extends `AUFR.`
- `AUFR. HALĀY. Ind.` ← extends `AUFR.`
- `AUFRECHT, HALĀY. Ind.` ← extends `AUFRECHT, HALĀY.`
- `AUFRECHT, UṆĀDIS. Ind.` ← extends `AUFRECHT`
- `AUFRECHTʼs Ausg. des HALĀY.` ← extends `AUFRECHT`
- `As. J. new s.` ← extends `As. J. new`
- `BAER und HELMERSEN, Beitr. z. Kenntn. d. russ. Reiches` ← extends `BAER`
- `BENF. SV.` ← extends `BENF.`
- `BENF. Uebers.` ← extends `BENF.`
- `BENFEY Chr.` ← extends `BENFEY`
- `BENFEY, Glossar z. SV.` ← extends `BENFEY`
- `BENFEY, SV. Einl.` ← extends `BENFEY, SV.`
- `BENFEY, SV. Vorr.` ← extends `BENFEY, SV.`
- `BENFEYʼs Dict.` ← extends `BENFEY`

### first 25 totally-uncited deleted candidates
- `?`
- `A Gloss. of jud. and rev. terms`
- `A. C. BURNELL`
- `ADHIMĀS.`
- `AGAYAPĀLA`
- `AH.`
- `ALBY.`
- `ALBYROUNY'S`
- `AMṚTAV. UP.`
- `AMṚTAVINDŪP.`
- `ANANDAL.`
- `ANANTASAM̃HITĀ`
- `ANEKĀRTHAKOŚA`
- `ANUKRAM.`
- `APAG. AV.`
- `AR. UP.`
- `ARHANT'S`
- `ARYABH.`
- `AUFRECHT'S`
- `AUSH.`
- `Abh. d. Königl. Ak. d. W. zu Berlin,`
- `Ak. d. Ww.`
- `Alg.`
- `As. Soc. of B.`
- `As. Soc. of Beng.`
