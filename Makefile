NAME=
QUICKLISP=~/quicklisp
XLSX=/Volumes/data/work/git/xlsx.git

CONFIG=config/$(NAME).yml
VERSION=$(shell git log --pretty=oneline | wc -l | sed 's/ //g')
DMGDEST=newsf-$(NAME)-$(VERSION)
SRCDEST=newsf-$(NAME)-source-$(VERSION)
ANALYSISDEST=sf-analysis-$(VERSION)
WXDEST=modelserver-$(NAME)-$(VERSION)
REPLAYDEST=replay-$(NAME)-$(VERSION)

PYTHON=python

all: source binary

source: $(SRCDEST).tgz

$(SRCDEST).tgz:
	git archive --format=tar --prefix=$(SRCDEST)/ HEAD | gzip -9 > builds/$(SRCDEST).tgz

binary:
	cd src && $(PYTHON) setup.py py2app
	mkdir -p builds/$(DMGDEST)/$(DMGDEST)
	mkdir builds/$(DMGDEST)/$(DMGDEST)/config
	mkdir builds/$(DMGDEST)/$(DMGDEST)/data
	mv src/dist/PSF.app builds/$(DMGDEST)/$(DMGDEST)
	cp $(CONFIG) builds/$(DMGDEST)/$(DMGDEST)/config/space-fortress.yml
	rm -f builds/$(DMGDEST).dmg
	hdiutil create -srcfolder builds/$(DMGDEST) builds/$(DMGDEST).dmg
	rm -r builds/$(DMGDEST)

wxmodel:
	cd src && $(PYTHON) wxmodel_setup.py py2app
	mkdir -p builds/$(WXDEST)/$(WXDEST)
	mkdir builds/$(WXDEST)/$(WXDEST)/config
	mkdir builds/$(WXDEST)/$(WXDEST)/data
	mv src/dist/ModelServer.app builds/$(WXDEST)/$(WXDEST)
	cp $(CONFIG) builds/$(WXDEST)/$(WXDEST)/config/space-fortress.yml
	rm -f builds/$(WXDEST).dmg
	hdiutil create -srcfolder builds/$(WXDEST) builds/$(WXDEST).dmg
	rm -r builds/$(WXDEST)

replay:
	cd src && $(PYTHON) replay_setup.py py2app
	mkdir -p builds/$(REPLAYDEST)/$(REPLAYDEST)
	mkdir builds/$(REPLAYDEST)/$(REPLAYDEST)/data
	mv src/dist/Replay.app builds/$(REPLAYDEST)/$(REPLAYDEST)
	rm -f builds/$(REPLAYDEST).dmg
	hdiutil create -srcfolder builds/$(REPLAYDEST) builds/$(REPLAYDEST).dmg
	rm -r builds/$(REPLAYDEST)


.PHONY: analysis
analysis:
	mkdir -p $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/cl-ppcre-2.0.3 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/flexi-streams-1.0.7 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/salza2-2.0.8 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/trivial-gray-streams-20110522-cvs $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/zip-20101107-cvs $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/cl-vectors-20101006-git $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/zpb-ttf-1.0.2 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/zpng-1.2.1 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/dists/quicklisp/software/vecto-1.4.4 $(ANALYSISDEST)/contrib
	cp -R $(QUICKLISP)/asdf.lisp $(ANALYSISDEST)/
	mkdir $(ANALYSISDEST)/contrib/xlsx/
	cp $(XLSX)/*.lisp $(ANALYSISDEST)/contrib/xlsx/
	cp $(XLSX)/xlsx.asd $(ANALYSISDEST)/contrib/xlsx/
	cp analysis/{analysis.lisp,loader.lisp,sf-analysis.asd,sflog.lisp,svg.lisp,visual-analysis.lisp,sans.ttf} $(ANALYSISDEST)
	mkdir $(ANALYSISDEST)/doc/
	cp analysis/doc/sf-analysis.{rst,html} $(ANALYSISDEST)/doc/
	hdiutil create -srcfolder $(ANALYSISDEST) $(ANALYSISDEST).dmg

.PHONY: clean
clean:
	rm -f builds/newfs-$(NAME)-source-*.tgz
	rm -f builds/newfs-*.dmg
