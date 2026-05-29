# Liturgics YAML Specification

This document describes the YAML format used to define Liturgics output PDFs.

## Overview

Each project YAML file describes one output PDF: a cover page, table of contents, ordered content components, signature padding, and printed page numbers. Run the build script against a project file:

```bash
pip install -r requirements.txt
cp .env.example .env   # set LITURGICS_LIBRARY_BUCKET for library-pdf components
python scripts/build.py projects/divine-liturgy.yaml
```

Output is written to `out/{Filename}`. Environment variables are read from the process environment and from a `.env` file at the repository root.

## Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `Name` | Yes | Title shown centered on the cover page |
| `Subtitle` | No | Subtitle shown below the title on the cover |
| `Description` | No | Metadata only; not rendered in the PDF (v1) |
| `Filename` | Yes | Output filename, written to `out/{Filename}` |
| `Components` | Yes | Ordered list of content blocks |

### Example

```yaml
Name: Divine Liturgy
Subtitle: TBD

Description: TODO

Filename: divine-liturgy.pdf

Components:
  - Key: GreatDoxology
    Name: Great Doxology
    TocExempt: false
    Type: library-pdf
    Path: orthros/great-doxology/doxology-tone-1.pdf
    Pages:
      Start: 2
    Side: recto
```

## Component fields

| Field | Required | Description |
|-------|----------|-------------|
| `Key` | Yes | Stable identifier; must be unique within the project |
| `Name` | Yes | Display name used in the table of contents |
| `TocExempt` | No | When `true`, omit from the TOC (default: `false`) |
| `Type` | Yes | Source type: `library-pdf`, `local-pdf`, or `local-md` |
| `Path` | Yes | Source path (see path rules below) |
| `Pages` | No | Optional page range from the source file |
| `Pages.Start` | No | First page to include (1-based, inclusive) |
| `Pages.End` | No | Last page to include (1-based, inclusive) |
| `Side` | No | Required side for the component's first page: `verso` or `recto` |

If `Pages` is omitted, the entire source file is included. If only `Start` is given, pages run from `Start` through the end of the file. If only `End` is given, pages run from page 1 through `End`.

## Component types

### `local-pdf`

Path is relative to the **repository root**. The file must exist locally.

```yaml
Type: local-pdf
Path: fixtures/sample.pdf
```

### `library-pdf`

Path is relative to the root of an S3 bucket. The bucket name is read from the `LITURGICS_LIBRARY_BUCKET` environment variable. Files are downloaded to `.cache/library/` during the build.

```yaml
Type: library-pdf
Path: orthros/great-doxology/doxology-tone-1.pdf
```

Set these in `.env` at the repository root (see `.env.example`) or in your shell environment:

- `LITURGICS_LIBRARY_BUCKET` — S3 bucket name (required for `library-pdf`)
- `AWS_REGION` — optional AWS region for boto3 (otherwise the default credential chain applies)

AWS credentials must be available through the standard boto3 credential chain (environment variables, shared config, instance role, etc.).

### `local-md`

Markdown sources for Jinja rendering. **Not yet implemented** — the build will fail with a clear error if a project includes `local-md` components.

## Page layout conventions

Liturgics uses a booklet page model based on **leaves** (sheets):

- **Recto** — the front of a leaf.
- **Verso** — the back of a leaf.

When pages are laid out sequentially in the PDF, each leaf contributes two pages: front then back.

- **Odd pages are recto** (front).
- **Even pages are verso** (back).

When the booklet is open, recto pages appear on the right and verso pages on the left (Western convention).

- The **cover** is physical page 1 (recto — the front of the first leaf). It is not numbered.
- A **blank verso page** is inserted immediately after the cover (physical page 2 — the back of the cover leaf). It is not numbered.
- The **table of contents** follows. TOC pages are not numbered.
- **Printed page 1** is always on a **recto** page — the first recto after the TOC ends. A blank recto is inserted after the TOC when necessary.
- **Odd printed pages are recto; even printed pages are verso.**
- If the first component must start on **verso** (`Side: verso`), a blank recto (printed page 1) is inserted before it; the component begins on the following verso (printed page 2).
- **Page numbers** appear in the footer outside margin: bottom-right on recto pages, bottom-left on verso pages. Numbering continues on all subsequent pages.

### `Side`

When `Side` is set, blank pages are inserted before the component if needed so its first page lands on the required side (`verso` or `recto`).

For the **first** component with `Side: verso`, a blank recto (printed page 1) is inserted before it; the component begins on printed page 2. For `Side: recto`, the component may begin directly on printed page 1 when it falls on the first recto after the TOC.

### Signature padding

Blank pages are appended at the end of the document so the total page count (cover, TOC, content, and padding) is divisible by **4**, suitable for booklet printing.

## Table of contents

The TOC lists every component except those with `TocExempt: true`. Each entry shows the component `Name` and the **printed** page number where that component begins.

Because TOC length affects physical page positions, the build performs a planning pass that estimates TOC size, computes component page numbers, renders the TOC, and re-plans if the TOC page count changes.

## Offline smoke testing

The example [`projects/divine-liturgy.yaml`](../projects/divine-liturgy.yaml) uses a `library-pdf` component. To test without S3 access, create a local PDF and point a copy of the project at it:

```yaml
Type: local-pdf
Path: fixtures/sample.pdf
```

Generate a sample fixture:

```bash
python3 -c "
from io import BytesIO
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

path = Path('fixtures/sample.pdf')
path.parent.mkdir(exist_ok=True)
pages = []
for i in range(3):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(72, 720, f'Sample page {i + 1}')
    c.showPage()
    c.save()
    pages.append(buf.getvalue())
writer = PdfWriter()
for page_data in pages:
    for page in PdfReader(BytesIO(page_data)).pages:
        writer.add_page(page)
out = BytesIO()
writer.write(out)
path.write_bytes(out.getvalue())
"
```

Then build with a YAML file that references `fixtures/sample.pdf` as a `local-pdf` component.

## YAML formatting

Use **spaces** for indentation (not tabs). Quote strings only when necessary.
