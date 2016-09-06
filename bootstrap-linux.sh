#!/bin/bash
# Author: askeing
# Version: 0.0.1


func_log () {
    echo "$@" | tee -a bootstrap-linux.log
}

################
# Prerequisite #
################

RET_SUCCESS="0"

func_log "[START] `date +%Y-%m-%d:%H:%M:%S`"

# OS Platform
PLATFORM=`uname`
if [[ ${PLATFORM} == 'Linux' ]]; then
    func_log "[INFO] Your platform is Linux."
elif [[ ${PLATFORM} == 'Darwin' ]]; then
    func_log "[FAIL] Your platform is Mac OS X, not Linux."
    exit 1
else
    func_log "[FAIL] Your platform is $PLATFORM not Linux."
    exit 1
fi


func_log "[INFO] Install Requiremants ..."
# tools
sudo apt-get install -y --force-yes unzip wget git
# python
sudo apt-get install -y --force-yes python-dev python-virtualenv python-pip
# build toolchains
sudo apt-get install -y build-essential cmake libffi-dev libssl-dev
# req of numpy, scipy
sudo apt-get install -y --force-yes libblas-dev liblapack-dev libatlas-base-dev gfortran
# opencv
sudo apt-get install -y --force-yes libopencv-dev python-opencv
func_log "[INFO] Install Requiremants finished."

################
# Installation #
################

func_log "[INFO] Creating virtualenv ..."
virtualenv .env-python
source .env-python/bin/activate

func_log "[INFO] Upgrading pip itself ..."
pip install -U pip
pip install -U setuptools

func_log "[INFO] Install numpy and scipy ..."
pip install numpy scipy

func_log "[INFO] Linking opencv's cv2.so to virtualenv ..."
CV2_SO_PATH=`find /usr/ -name "cv2.so" -print | head -n 1`  # only get first result
ln -s ${CV2_SO_PATH} .env-python/lib/python2.7/site-packages/cv2.so

func_log "[INFO] Python Setup Install ..."
pip install -r requirements.txt
python setup.py install

func_log "[INFO] Checking Python CV2 Module ..."
PYTHON_CV2_CHECK_RESULT=`./scripts/cv2_checker.py`
BOOTSTRAP_RET=$?
func_log ${PYTHON_CV2_CHECK_RESULT}

func_log "[INFO] Done."
func_log "[END] `date +%Y-%m-%d:%H:%M:%S`"
func_log ""

if [[ ${RET_SUCCESS} == ${BOOTSTRAP_RET} ]]; then
    func_log "### Hasal ##############"
    func_log "# Welcome to Hasal! :) #"
    func_log "########################"
    func_log ""
else
    func_log "### Hasal ########################"
    func_log "# It seems like something wrong! #"
    func_log "# Please check bootstrap log.    #"
    func_log "##################################"
    func_log ""
    exit 1
fi

