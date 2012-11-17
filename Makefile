##
## Created       : Sat Nov 17 14:46:20 IST 2012
## Last Modified : Sat Nov 17 15:05:41 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## This file is part of PRS
##
## PRS is free software: you can redistribute it and/or modify it under
## the terms of the GNU Affero General Public License as published by the
## Free Software Foundation, version 3 of the License
##
## PRS is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
## License for more details.
##
## You should have a copy of the license in the base directory of PRS.  If
## not, see <http://www.gnu.org/licenses/>.

##
## You do not need to use this Makefile to run the program. If all you
## want to do is to use PRS, there is nothing here.
##
## This Makefile automates some of the steps in the release
## process. Ideally we want to automate all of the following setps
## based on a version string, which is also used to tag the source repo
##
##  1. Change the version string in prs.pyw
##
##  2. Commit the above change
##
##  3. Tag the source with the version number
##
##  4. Clone the current repo into a temporary repository
##
##  5. cd to the repository and build the documentation
##
##  6. Zip up the repository into .zip and .tar.gz archives
##
##  7. Upload the archives to github downloads section
## 
##  8. Edit the announcements in gae/index.html, and update the
##     timestamp for the page in the footer.
##
##  9. Push the updates to gae
##
## 10. Change the version with a '+' added to the version string.
##
## 11. Commit the changes
##
## 12. Push changes to upstream git repo
##
## The steps that involve pushing things to github and gae will come
## under the 'install' target. The rest will come under the default
## target. There is nothing to clean up at this stage.
##

src = ../asynk.py
basename = cmc

default: bundle

bundle:
ifeq ($(strip ${TAG}),)
	$(error "Have to specify a tag to bundle. Usage: 'make TAG=<rel>'")
endif
	@echo
	@echo ==== Cloning temp repository for ${TAG}
	rm -rf /tmp/${basename}-${TAG}
	git clone --recursive . /tmp/${basename}-${TAG}
	cd /tmp/${basename}-${TAG}
	git checkout ${TAG}
	rm -rf /tmp/${basename}-${TAG}/.git

	@echo
	@echo ==== Creating bundles
	rm -f /tmp/${basename}-${TAG}.zip
	cd /tmp && zip -q -r ${basename}-${TAG}.zip ${basename}-${TAG}

release:
ifeq ($(strip ${REL}),)
	$(error "Have to specify a release. Usage: 'make REL=<rel>'")
endif
	@echo
	@echo ==== Replacing version identifier in ${src}...
	sed -i .bak "s/^asynk_ver = \'.*\'/asynk_ver = \'${REL}\'/" ${src}

	@echo ==== Comitting change to repository...
	git add ${src}
	cd .. && git commit -m 'Bumping up version to ${REL} for release'

	@echo
	@echo ==== Tagging release with ${REL}...
	cd .. && git tag -a -m 'Release ${REL}' ${REL}

	@echo
	@echo ==== Cloning temp repository for ${REL}
	rm -rf /tmp/asynk-${REL}
	cd .. && git clone . /tmp/asynk-${REL}
	rm -rf /tmp/asynk-${REL}/.git

	@echo
	@echo ==== Building documentation...
	cd /tmp/asynk-${REL}/doc/ && make

	@echo
	@echo ==== Creating bundles
	rm -f /tmp/asynk-${REL}.tar*
	rm -f /tmp/asynk-${REL}.zip
	cd /tmp && tar -cvf asynk-${REL}.tar.gz -z  asynk-${REL} > /dev/null 2>&1
	cd /tmp && zip -q -r asynk-${REL}.zip asynk-${REL}

	@echo
	@echo "**********************"
	@echo "*****   Success  *****"
	@echo 
	@echo Bundles available here:
	@echo
	ls -ldh /tmp/asynk-${REL}*

install:
	@echo
	@echo ==== Pushing release changes with tags upstream...
	cd .. && git push --tags

	@echo
	@echo ==== Replacing version identifier in ${src} to dev ver...
	sed -i .bak "s/^asynk_ver = \'.*\'/asynk_ver = \'${REL}+\'/" ${src}

	@echo ==== Comitting change to repository...
	git add ${src}
	cd .. && git commit -m 'Bumping up version to ${REL}+ for development'
