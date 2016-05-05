#!/bin/bash
# Author: askeing
# Version: 0.0.4
#
# fork from
# https://gist.github.com/askeing/3b138fd0bff112f009178d92e0c2d875#file-install_hasal-sh

pushd ~

echo "# Install prerequisites..."
sudo apt-get -y install python2.7-dev
sudo apt-get -y install python-setuptools
sudo apt-get -y install python-virtualenv
sudo apt-get -y install wget libav-tools libavc1394-0 mencoder libavahi-common-data

sudo apt-get -y install ppa-purge
sudo ppa-purge ppa:jon-severinsson/ffmpeg
yes | sudo add-apt-repository ppa:mc3man/trusty-media

sudo apt-get -y update
sudo apt-get -y dist-upgrade
sudo apt-get -y install ffmpeg
sudo apt-get -y install libavformat-extra-54
sudo apt-get -y install libavfilter3
sudo apt-get -y install libavutil-extra-52
sudo apt-get -y install build-essential cmake git pkg-config
sudo apt-get -y install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libatlas-base-dev gfortran
sudo apt-get -y install vim
sudo apt-get -y install wmctrl
sudo apt-get -y install default-jre
sudo apt-get -y install default-jdk
sudo apt-get -y install xdotool
sudo apt-get -y install libopencv-core2.4
sudo apt-get -y install libopencv-highgui2.4
sudo apt-get -y install libtesseract3

sudo easy_install pip
sudo pip install virtualenv virtualenvwrapper
sudo rm -rf ~/.cache/pip

if [[ ! -d ~/.hasalenv ]]
then
    echo "# Create .hasalenv virtualenv..."
    virtualenv ~/.hasalenv
    source ~/.hasalenv/bin/activate
    pip install numpy

    echo "# Set up virtualenvwrapper..."
    echo "# virtualenv and virtualenvwrapper" >> ~/.bashrc
    echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc

    source ~/.bashrc
else
    echo "# Already have .hasalenv virtualenv... Skip"
    source ~/.hasalenv/bin/activate
fi

if [[ ! -d ~/opencv ]]
then
    echo "# Make opencv and opencv_contrib..."
    cd ~
    git clone https://github.com/Itseez/opencv.git
    pushd opencv
    git checkout 3.0.0
    popd
    git clone https://github.com/Itseez/opencv_contrib.git
    pushd opencv_contrib
    git checkout 3.0.0
    popd

    pushd opencv
    mkdir build
    pushd build
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D INSTALL_C_EXAMPLES=ON \
        -D INSTALL_PYTHON_EXAMPLES=ON \
        -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
        -D BUILD_EXAMPLES=ON ..
    make -j4
    sudo make install
    sudo ldconfig
    popd
    popd

    echo "# Linking cv2.so to .hasalenv virtualenv..."
    pushd ~/.hasalenv/lib/python2.7/site-packages/
    ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
    popd
else
    echo "# Already have opencv and opencv_contrib... Skip"
fi

if [[ ! -d ~/sikulix ]]
then
    echo "# Install sikulix..."
    cd ~
    mkdir sikulix
    pushd sikulix
    wget https://launchpad.net/sikuli/sikulix/1.1.0/+download/sikulixsetup-1.1.0.jar
    chmod a+x sikulixsetup-1.1.0.jar
    java -jar sikulixsetup-1.1.0.jar
    popd
else
    echo "# Already have sikulix... Skip"
    ls ~/sikulix
fi

if [[ ! -d ~/Hasal ]]
then
    echo "# Clone Hasal project..."
    cd ~
    git clone https://github.com/Mozilla-TWQA/Hasal.git
else
    echo "# Already have Hasal project... Skip"
fi
    cd ~
    pushd Hasal
    pushd thirdParty
    echo "# Get latest xpi files..."
    rm -rf *.xpi *.zip sikulix
    wget https://github.com/bgirard/Gecko-Profiler-Addon/raw/master/geckoprofiler-signed.xpi
    wget https://addons.mozilla.org/firefox/downloads/file/425008/perf_mark_of_add_on_start_and_end_for_google_docs-0.0.1-fx+an.xpi
    wget https://github.com/Itseez/opencv/archive/3.0.0.zip
    cp -r ~/sikulix ./sikulix
    popd
    pip install -Ur requirements.txt
    popd

popd

echo "===================="
echo "Welcome to Hasal! :)"
echo "        - by askeing"

