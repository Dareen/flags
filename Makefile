APP_NAME = flags
IMAGE_NAME ?= dubizzledotcom/$(APP_NAME)
IMAGE_VERSION ?= $(shell docker/tag_helper.sh)
SOURCE_BUNDLE_ARCHIVE_NAME = $(APP_NAME)-$(IMAGE_VERSION).zip
SHELL = /bin/bash
GIT_BRANCH = $(shell git rev-parse HEAD)
FLAGS_GIT_REPO = git@github.com:dubizzle/$(APP_NAME)


.PHONY: docker


docker-local: docker-prep
	cat requirements/base.txt requirements/development.txt requirements/testing.txt  > docker/requirements.txt
	tar -pczf docker/archive.tar.gz . --exclude-vcs --exclude=docker/archive.tar.gz --exclude="temp_*" --exclude="*.pyc" --exclude="local_settings.py"
	$(MAKE) docker-common

docker-git: docker-prep
	cp -p requirements/base.txt docker/requirements.txt
	git clone $(FLAGS_GIT_REPO) docker/$(APP_NAME)
	cd docker/$(APP_NAME); git reset --hard $(GIT_BRANCH); git submodule update --init
	cd docker/$(APP_NAME); tar --exclude=.git -zcvf ../archive.tar.gz .
	$(MAKE) docker-common

docker-common:
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) docker
	-rm -rf docker/archive.tar.gz docker/requirements.txt docker/$(APP_NAME)

docker-prep: clean-docker
	mkdir docker/$(APP_NAME)

docker: docker-git

clean-docker:
	-rm -rf docker/archive.tar.gz docker/requirements.txt docker/$(APP_NAME)

docker-push:
	docker push $(IMAGE_NAME):$(IMAGE_VERSION)

beanstalk-source-bundle:
	cp docker/Dockerrun.aws.json.tpl docker/Dockerrun.aws.json
	sed -i 's|{{ IMAGE_NAME }}|$(IMAGE_NAME)|' docker/Dockerrun.aws.json
	sed -i 's|{{ IMAGE_VERSION }}|$(IMAGE_VERSION)|' docker/Dockerrun.aws.json
	mkdir -p target
	cd docker && zip -FSr ../target/$(SOURCE_BUNDLE_ARCHIVE_NAME) Dockerrun.aws.json

clean-beanstalk:
	-rm -rf target
	-rm -f docker/Dockerrun.aws.json

clean: clean-docker clean-beanstalk
