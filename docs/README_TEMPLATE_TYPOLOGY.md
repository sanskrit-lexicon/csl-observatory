# README template typology

This note defines the README patterns to use across Sanskrit Lexicon
repositories.  The intended style is practical and Jim-like: say what the
repository is, where the data comes from, which files matter, how the work is
done, what commands have actually been used, and what remains uncertain.

Do not turn these into marketing pages.  A good README here is closer to a
field notebook than a product brochure.

## Regeneration-safe contract

Human-maintained README material belongs inside manual blocks:

```markdown
<!-- BEGIN MANUAL: overview -->
...human-maintained overview, workflow, commands, caveats...
<!-- END MANUAL: overview -->
```

Generated issue counts, Mermaid charts, and label taxonomy summaries may follow
the manual block.  Runbooks and automation must preserve every block matching
`<!-- BEGIN MANUAL:* -->` through the corresponding `<!-- END MANUAL:* -->`
verbatim.

Recommended guard for important repositories:

```yaml
name: README manual overview guard

on:
  pull_request:
    paths: [README.md]
  push:
    branches: [master, main]
    paths: [README.md]
  workflow_dispatch:

jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify manual overview block
        run: |
          grep -qF '<!-- BEGIN MANUAL: overview' README.md
          grep -qF '<!-- END MANUAL: overview -->' README.md
          for heading in '## Primary data' '## Directories' '## How work is done'; do
            grep -qF "$heading" README.md
          done
```

Adjust required headings for the repo archetype.

## Template A: dictionary correction / workbench repo

Use for dictionary-specific repositories such as `VCP`, `ApteES`, `SCH`,
`BHS`, `CAE`, `CCS`, `STC`, `VEI`, `MCI`, `ACC`, and `LRV`.

````markdown
# CODE - Full Dictionary Name

<!-- BEGIN MANUAL: overview -->
CODE is the working repository for ...  The canonical source text is ...
This repository contains scripts, notes, and issue folders used to improve the
CDSL representation of the printed dictionary.

## Primary data

| Item | Location | Notes |
|---|---|---|
| Canonical CDSL source | `csl-orig/v02/code/code.txt` | Edited through documented changes, not ad hoc. |
| Local work files | `...` | ... |
| Scans / source edition | `...` | ... |

## Directories

| Path | Purpose |
|---|---|
| `issues/` | One folder per issue; read the local `readme.txt` first. |
| `verbs01/` | Verb/preverb analysis, if present. |

## Major workflows

| Workflow | Paths | Result |
|---|---|---|
| ... | ... | ... |

## How work is done

Most changes follow this pattern:

```text
source text -> analysis script -> change/log file -> review -> csl-orig update
```

Corrections should be traceable to an issue folder, a `readme.*` note, or a
change file.

## Common commands

```sh
sh redo.sh
python script.py
```

Use only commands that are present in the repository.

## Data format

The source follows standard CDSL markup: `<L>` entry ids, `<k1>` primary
headwords, `<k2>` variants, `<pc>` page/column data, `<ls>` literary sources,
and `<ab>` abbreviations.  Add dictionary-specific caveats here.

## Current status / open questions

- ...
<!-- END MANUAL: overview -->
````

Small repos may omit `Major workflows`.  Verb/preverb-focused repos should keep
a short `## Verb work` subsection under the manual block.

## Template B: correction hub repo

Use for `CORRECTIONS`.

````markdown
# CORRECTIONS

<!-- BEGIN MANUAL: overview -->
CORRECTIONS is the cross-dictionary staging area for correction evidence,
historical notes, forms, and batch-preparation files.

## Where to put a correction

| Path | Use |
|---|---|
| `daily/` | Daily correction intake and review material. |
| `dictionaries/` | Dictionary-specific preparation work. |
| `english_error/` | English-language error reports and checks. |
| `k1k2/` | Headword and secondary-headword checks. |
| `ngram/` | N-gram based candidate discovery. |
| `sanhw1/`, `sanhw2/` | Sanskrit headword review material. |

## Correction lifecycle

```text
candidate -> correction note/form -> review -> change file/script -> target repo
```

## Important files

List historical files, forms, spreadsheets, and scripts that should not be
moved without provenance notes.

## Do not edit blindly

Preserve historical evidence.  New edits should say which dictionary, source
record, issue, and review step they belong to.
<!-- END MANUAL: overview -->
````

## Template C: canonical source data repo

Use for `csl-orig`.

````markdown
# csl-orig

<!-- BEGIN MANUAL: overview -->
`csl-orig` is the canonical source-text repository for CDSL dictionaries.

## Repository topology

| Path | Role |
|---|---|
| `v02/<dict>/<dict>.txt` | Canonical dictionary source text. |
| `v02/<dict>/althws/` | Alternate-headword material. |
| `v02/<dict>/<workdir>/` | Dictionary-specific preparation notes/scripts. |

## How corrections arrive

Corrections usually come from dictionary workbench repos, `csl-corrections`, or
issue-specific scripts in this repository.

## Editing policy

Avoid unlogged direct edits.  A change should be traceable to an issue, local
README/readme note, generated change file, or script.

## Build/display relation

`csl-pywork`, `csl-app`, `csl-apidev`, and web display repositories consume
this source.

## Hybrid issue taxonomy

Dictionary labels and tooling labels may coexist here because this repository
is both a data store and the central correction target.
<!-- END MANUAL: overview -->
````

## Template D: build / pywork repo

Use for `csl-pywork`.

````markdown
# csl-pywork

<!-- BEGIN MANUAL: overview -->
`csl-pywork` contains per-dictionary build scripts and generated-work
preparation used by the CDSL pipeline.

## Input and output

| Direction | Location | Notes |
|---|---|---|
| Input | `csl-orig/v02/...` | Canonical source text. |
| Output | XML, SQLite, reports | Generated or checked artifacts. |

## Directory map

Explain `v00/`, `v02/`, `distinctfiles/`, templates, and issue folders.

## Typical build flow

```text
csl-orig source -> per-dictionary pywork -> validation/logs -> generated output
```

## Per-dictionary conventions

Most detailed notes live under the dictionary-specific work directory.  Read
local `readme.*` files before changing scripts.

## Common failure modes

Encoding drift, stale generated files, missing sibling repos, and path
assumptions on Windows versus Cologne servers.
<!-- END MANUAL: overview -->
````

## Template E: web frontend / runtime repo

Use for `csl-websanlexicon`.

````markdown
# csl-websanlexicon

<!-- BEGIN MANUAL: overview -->
This repository contains the web display/runtime material for the public CDSL
site.

## Runtime surfaces

List the live display folders, templates, static assets, and legacy backup
areas.

## Architecture map

Separate current code from archived backups.  Say which version should be used
for new work.

## Local inspection / deploy notes

Give only verified commands and known server paths.

## Relation to sibling repos

Explain how `csl-apidev`, `csl-app`, `csl-orig`, and `csl-pywork` feed or
consume this repository.

## Known legacy zones

Mark backup/archival folders explicitly so future cleanup work does not treat
them as current code.
<!-- END MANUAL: overview -->
````

## Template F: research / comparison repo

Use for `Wil-YAT` and similar comparison studies.

Keep the long methodological narrative.  Add only enough structure to help a
new maintainer resume:

```markdown
# Study name

<!-- BEGIN MANUAL: overview -->
Short summary.

## Inputs
## Outputs
## Workflow
## How to resume work
## Remaining work
<!-- END MANUAL: overview -->
```

Do not delete the older narrative unless it is duplicated by the new sections.
