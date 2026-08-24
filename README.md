# Resume

My resume. The data lives in one JSON file. The Markdown, the LaTeX, and the PDF are all
generated from it.

`resume.json` follows the [JSON Resume](https://jsonresume.org/schema/) v1 schema. That schema
is a standard, so other tools can read this file too.

## Layout

| Path | What it holds |
| --- | --- |
| `resume.json` | The source of truth. Edit only this file. |
| `scripts/render.py` | Turns the JSON into Markdown or LaTeX. |
| `templates/resume.tex.template` | The LaTeX page design. |
| `build/` | The generated Markdown, LaTeX, and PDF. |
| `.github/workflows/build.yml` | Builds and checks the output on each push. |

## How to build

You need Python 3. For the PDF you also need a LaTeX engine, and for the pandoc path you need
pandoc.

```sh
brew install pandoc tectonic    # macOS
make all                        # Markdown, LaTeX, and PDF
```

Single targets:

```sh
make md            # build/resume.md
make tex           # build/resume.tex
make pdf           # build/resume.pdf with tectonic
make pdf-pdflatex  # build/resume.pdf with a TeX Live install
make pandoc-tex    # build/resume-pandoc.tex from the Markdown
make check         # make sure resume.json is valid
make clean         # remove build/
```

## The two LaTeX paths

There are two ways to get LaTeX out of this repo. They serve different needs.

1. `make tex` reads the JSON and fills in `templates/resume.tex.template`. This path gives the
   real resume design: right-aligned dates, small caps section names, and a one page fit. Use
   this path for anything you send to a person.
2. `make pandoc-tex` converts `build/resume.md` with pandoc. This path gives a plain document
   with the standard pandoc article style, and it runs to two pages. Use it when you want a
   quick, generic conversion, or when you want another output format that pandoc supports.

## How to update the resume

1. Edit `resume.json`.
2. Run `make all`.
3. Check `build/resume.pdf`.
4. Commit the JSON and the files in `build/`.

Dates use the `YYYY-MM` form. Set `endDate` to `null` for a job you still hold. The renderer
prints `Present` for a null end date.
