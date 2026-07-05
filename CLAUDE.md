# Liturgics

A liturgical service book builder for St Catherine Orthodox Church. Source files are markdown components and project YAML files; the build pipeline assembles them into PDFs.

## Building

Always use the project `.venv`:

```
.venv/bin/python scripts/build.py <path-to-project-yaml>
```

Output is written to `out/`. To build all projects:

```
for f in projects/*.yaml; do .venv/bin/python scripts/build.py "$f"; done
```

## Project files

Each file in `projects/` defines one service book:

- `baptism.yaml` — Holy Baptism
- `communion-faithful.yaml` — Communion of the Faithful
- `daily-orthros.yaml` — Daily Orthros (weekday mornings)
- `divine-liturgy.yaml` — Divine Liturgy of St John Chrysostom / St Basil
- `episcopal.yaml` — Episcopal services
- `great-vespers.yaml` — Great Vespers (Saturday evenings / feast eves)
- `sunday-orthros.yaml` — Sunday/Festal Orthros
- `typika.yaml` — Typika

## Structure

```
projects/       # One YAML per service book
components/     # Markdown fragments, organized by service
  common/       # Shared across multiple services
  divine-liturgy/
  orthros/
  vespers/
  baptism/
  ...
scripts/        # Build pipeline
out/            # Build artifacts (not committed)
```

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

Common `Config` flags (used by psalm components):
- `repeat` — print the psalm twice
- `glory` — append a Glory doxology
- `alleluia` — append Alleluia verses
- `god_and_hope` — append "God is the Lord" / "My hope is the Father" ending
- `lord_have_mercy_glory` — append a Lord-have-mercy / Glory transition

## Important

**Do not modify liturgical text without being explicitly asked to.** The texts in `components/` are established liturgical translations used in worship. Typo fixes or formatting changes are fine; rewording is not.
