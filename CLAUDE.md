# Liturgics

A liturgical service book builder for St Catherine Orthodox Church. Source files are markdown components and project YAML files; the build pipeline assembles them into PDFs.

## Building

Always use the project `.venv`:

```
.venv/bin/python scripts/build.py <path-to-project-yaml>
```

Output is written to `out/`. To build all projects:

```
for f in projects/choir-books/*.yaml; do .venv/bin/python scripts/build.py "$f"; done
```

## Project files

Choir book project YAMLs live in `projects/choir-books/`:

- `baptism.yaml` — Holy Baptism
- `communion-faithful.yaml` — Communion of the Faithful
- `daily-orthros.yaml` — Daily Orthros (weekday mornings)
- `divine-liturgy.yaml` — Divine Liturgy of St John Chrysostom / St Basil
- `episcopal.yaml` — Episcopal services
- `great-vespers.yaml` — Great Vespers (Saturday evenings / feast eves)
- `hours.yaml` — The Hours
- `sunday-orthros.yaml` — Sunday Orthros
- `festal-orthros.yaml` — Festal Orthros
- `typika.yaml` — Typika

## Structure

```
projects/
  choir-books/  # One YAML per choir/service book
  booklets/     # One .tex per congregational booklet
components/     # Source fragments, organized by type and service
  divine-liturgy/  # Choir book markdown components
  common/          # Shared choir book components
  orthros/
  vespers/
  baptism/
  hours/
  booklets/        # LaTeX fragments for booklets
    common/        # Shared across multiple booklets (Creed, Lord's Prayer, etc.)
    divine-liturgy/
themes/
  booklet/
    preamble.tex  # LaTeX preamble / style definitions for booklets
scripts/        # Build pipeline
out/            # Build artifacts (not committed)
```

## Booklets

Congregational service booklets are LaTeX projects. Requires MacTeX (`brew install --cask mactex-no-gui`). The project file is the root LaTeX document and lives in `projects/booklets/`. It `\input{}`s the theme preamble and component fragments directly — no YAML or assembly step.

To build a booklet:

```
.venv/bin/python scripts/build_booklet.py projects/booklets/divine-liturgy.tex
```

To build all booklets:

```
for f in projects/booklets/*.tex; do .venv/bin/python scripts/build_booklet.py "$f"; done
```

Booklet components are `.tex` files in `components/booklets/`. Reusable content (e.g. the Creed, Lord's Prayer) lives in `components/booklets/common/` so it can be shared across multiple booklets.

The LaTeX preamble at `themes/booklet/preamble.tex` defines all formatting commands:

- `\speak{Role}{text}` — role-label dialogue with hanging indent
- `\rubric{text}` — italic stage direction / rubric
- `\cross` — the cross symbol (✢) used before blessings and responses
- `\subsect{Title}` — bold subsection heading for named variants
- `\bookletcover{Title}{Subtitle}{Date}` — cover page
- `\bookletintro{body}{author}{date}` — introduction page
- `\bookletdate` — build-time revision date (injected by `build_booklet.py`, same format as choir-book covers). Use this instead of hardcoding dates on the cover/intro.

## Components

Markdown components use role labels to identify who speaks:

- `Priest:` / `Deacon/Priest:` — clergy
- `People/Choir:` — congregational response
- `Reader:` / `Choir:` — as appropriate

Components are plain markdown. Jinja templating (`{% %}`, `{{ }}`) is not used in components.

## Project YAML

Each project lists its components in order. Each component entry looks like:

```yaml
- Key: UniqueKey
  Name: Display Name
  Type: local-md        # or library-pdf
  Path: components/...  # relative to project root
  TocExempt: true       # omit from table of contents (optional)
  Side: verso           # force page side: recto or verso (optional)
  Config:               # component-level config flags (optional)
    repeat: true
```

`library-pdf` components are pre-built PDFs curated by the team in an S3 bucket. Do not modify their paths without knowing the bucket contents.

Psalm components use a template (`_templates/psalm.md`) controlled by `Config` flags. These flags append text after the psalm body:

- `repeat` — repeats a designated verse from the psalm's frontmatter in italics (used for the refrain at the end of a kathisma reading)
- `glory` — appends the Lesser Doxology: *Glory to the Father and to the Son and to the Holy Spirit; both now and ever and unto ages of ages. Amen.*
- `alleluia` — appends three *Alleluia. Alleluia. Alleluia. Glory to Thee, O God.* lines
- `god_and_hope` — appends *O our God and our Hope, glory to Thee!* (mutually exclusive with `lord_have_mercy_glory`)
- `lord_have_mercy_glory` — appends three *Lord, have mercy.* lines followed by the Lesser Doxology (mutually exclusive with `god_and_hope`)

## Important

**Do not modify liturgical text without being explicitly asked to.** The texts in `components/` are established liturgical translations used in worship. Typo fixes or formatting changes are fine; rewording is not.
