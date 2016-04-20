PYTHON := python
VENV := ~/.hasalenv

$(VENV)/bin/python:
	[ -d $(VENV) ] || $(PYTHON) -m virtualenv $(VENV) || virtualenv $(VENV)
	$(VENV)/bin/pip install --upgrade setuptools
	$(VENV)/bin/python setup.py develop


.PHONY: dev-env
dev-env: $(VENV)/bin/python


# for testing
.PHONY: test
test: dev-env
	$(VENV)/bin/python -m unittest tests.test_chrome_gdoc_create_copypaste_table_1

#####################################
# below are origin makrfile scripts #
#####################################
install: venv-install pip-install video-recording-libs-install

opencv-install:
	wget https://github.com/Itseez/opencv/archive/3.0.0.zip
	unzip ./3.0.0.zip
	sudo apt-get update
	sudo apt-get upgrade
	sudo apt-get install build-essential cmake git pkg-config
	sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
	sudo apt-get install libgtk2.0-dev
	sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	sudo apt-get install libatlas-base-dev gfortran

video-recording-libs-install:
	sudo apt-get install wget libav-tools ffmpeg libavc1394-0 libavformat-extra-53 libavfilter2 libavutil-extra-51 mencoder libavahi-common-data

venv-install:
ifndef VIRTUAL_ENV
	virtualenv venv
endif

cv2-install-venv:
	cd env/lib/python2.7/site-packages
	ln -s /usr/local/lib/python2.7/dist-packages/cv2.so cv2.so
	cd ../../..

pip-install:
	source venv/bin/activate
	pip install selenium
	pip install numpy

clean:
	find . -name "*.pyc" -type f -delete
	rm -rf output/images/output/*
	rm -rf output/images/sample/*
	rm -rf output/profiles/*
	rm -rf output/videos/*
	rm result.json
