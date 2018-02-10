##
## Created       : Thu May 17 13:02:14 IST 2012
## Last Modified : Sat Jul 28 09:16:51 IST 2012
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
## You should have a copy of the license with PRS.  If not, see
## <http://www.gnu.org/licenses/>.

##
## You do not need to use this Makefile to run the program. This
## Makefile automates some of the steps in the release
## process. 
##
##  1. Zip up the repository into .zip archive based on an existing tag
##

zip:
ifeq ($(strip ${TAG}),)
	$(error "Have to specify a release. Usage: 'make TAG=<rel>'")
endif

	@echo
	@echo ==== Cloning temp repository for ${TAG}
	rm -rf /tmp/cmc-${TAG}
	cd .. && git clone . /tmp/cmc-${TAG}

	@echo
	@echo ==== Checking out TAG ${TAG} ...
	cd /tmp/cmc-${TAG} && git checkout ${TAG}
	rm -rf /tmp/cmc-${TAG}/.git

	@echo
	@echo ==== Copying Databases ...
	cp ../db/* /tmp/cmc-${TAG}/db

	@echo
	@echo ==== Creating bundles
	rm -f /tmp/cmc-${TAG}.zip
	cd /tmp && zip -q -r cmc-${TAG}.zip cmc-${TAG}
	mv /tmp/cmc-${TAG}.zip ${HOME}/Dropbox/Nalini_Sriram/PrS/

	@echo
	@echo "**********************"
	@echo "*****   Success  *****"
	@echo 
	@echo Bundles available here:
	@echo
	ls -ldh ${HOME}/Dropbox/Nalini_Sriram/PrS/cmc*
