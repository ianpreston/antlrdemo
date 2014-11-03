BUILDDIR = interpreter/parse
ANTLR = java -jar /usr/local/lib/antlr-4.4-complete.jar


all: $(BUILDDIR)

$(BUILDDIR): Hello.bnf
	$(ANTLR) Hello.bnf -o $(BUILDDIR) -Dlanguage=Python2 -visitor
	touch $(BUILDDIR)/__init__.py
