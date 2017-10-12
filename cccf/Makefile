examples = \
  ccf

all: $(examples:%=%.pdf)

%.pdf: %.tex
	xelatex $(@:%.pdf=%.tex)
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

clean:
	rm -f *.aux *.log *.nav *.pdf *.out *.snm *.toc *.vrb

