# resume.json is the source of truth. Everything else is generated.

BUILD := build

.PHONY: all md tex pdf pdf-pdflatex pandoc-tex pandoc-pdf check clean

all: md tex pdf

$(BUILD):
	mkdir -p $(BUILD)

# JSON to Markdown.
md: | $(BUILD)
	python3 scripts/render.py --format md --output $(BUILD)/resume.md

# JSON to LaTeX, with the resume template in templates/.
tex: | $(BUILD)
	python3 scripts/render.py --format tex --output $(BUILD)/resume.tex

# LaTeX to PDF with tectonic. Tectonic gets the packages it needs on demand.
pdf: tex
	tectonic -X compile $(BUILD)/resume.tex --outdir $(BUILD)

# LaTeX to PDF with a normal TeX Live install. CI uses this target.
pdf-pdflatex: tex
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory $(BUILD) $(BUILD)/resume.tex
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory $(BUILD) $(BUILD)/resume.tex

# The pandoc path. Markdown to LaTeX, then to PDF.
pandoc-tex: md
	pandoc $(BUILD)/resume.md \
	  --standalone --from=markdown --to=latex \
	  --variable=geometry:margin=0.7in \
	  --variable=fontfamily:charter \
	  --variable=colorlinks:true \
	  --output=$(BUILD)/resume-pandoc.tex

pandoc-pdf: pandoc-tex
	tectonic -X compile $(BUILD)/resume-pandoc.tex --outdir $(BUILD)

check:
	python3 -c "import json;json.load(open('resume.json'));print('resume.json is valid JSON')"

clean:
	rm -rf $(BUILD)
