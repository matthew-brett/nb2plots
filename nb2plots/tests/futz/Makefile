BUILDDIR = build
SRCDIR = proj1

all: build-html

clean:
	rm -rf $(BUILDDIR)

init: clean
	rm -rf $(SRCDIR)
	cp -r ../$(SRCDIR) .

build-% :
	sphinx-build -W -b $* -d $(BUILDDIR) $(SRCDIR) $(BUILDDIR)

debug-% :
	sphinx-build -P -W -b $* -d $(BUILDDIR) $(SRCDIR) $(BUILDDIR)

permissive-% :
	sphinx-build -b $* -d $(BUILDDIR) $(SRCDIR) $(BUILDDIR)

html: build-html

doctest: build-doctest

text: build-text
