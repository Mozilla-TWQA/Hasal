# Hasal Performance Test

**Master**

[![Master Linux Status](https://img.shields.io/travis/Mozilla-TWQA/Hasal/master.svg?label=Linux/Mac%20build)](https://travis-ci.org/Mozilla-TWQA/Hasal)
[![Master Windows Status](https://img.shields.io/appveyor/ci/HasalDev/hasal/master.svg?label=Windows%20build)](https://ci.appveyor.com/project/HasalDev/hasal/branch/master)

**Dev**

[![Dev Linux Status](https://img.shields.io/travis/Mozilla-TWQA/Hasal/dev.svg?label=Linux/Mac%20build)](https://travis-ci.org/Mozilla-TWQA/Hasal)
[![Dev Windows Status](https://img.shields.io/appveyor/ci/HasalDev/hasal/dev.svg?label=Windows%20build)](https://ci.appveyor.com/project/HasalDev/hasal/branch/dev)

"**Hasal**" */ha'sɑlu/* this word is came from Indigenous Taiwanese "**Bunun**", and it means hail. Why we choose this word is because we expect our testing could like the hail, fast and weighty. And through our testing could bring more improvement on our performance or quality.

A Framework for testing web performance between different browser

## Automatical Installation
If you do not wish to install Hasal automatically, please proceed to next section "Manual Installation". For those who wants to install Hasal, please be notified that a clean environment or
* Ubuntu
```
.\bootstrap-linux.sh
```

* Mac OS
```
.\bootstrap-mac.sh
```

* Windows 7
Launch a command line console with administrator privilege.
```
bootstrap.bat
```

* Windows 8 or above
Launch a powershell console with administrator privilege.
```
Set-ExecutionPolicy Unrestricted
.\bootstrap.ps1
```
Please noted that Hasal in Windows systems can be run from command line only.

## Manual Installation
* Install Firefox
* Install SikluliX (https://launchpad.net/sikuli/sikulix/1.1.0), place the runsikulix and other installation files in hasal/thirdparty. When sikulix setup diaglog come out, please select the Pack 1 and make sure scripting language: Python is checked.
* Install video recording codes and libs (windows/mac:ffmpeg or ubuntu:avconv)
* Install video recording main program (windows/mac:ffmpeg or ubuntu:avconv)
* Install opencv
* Download the client certificate from here (https://goo.gl/yfki48 -- note: needs a mozilla.com account ATM), place all certificates in your hasal working dir. 
* Run setup.py

## For Ubuntu:
```
apt-get install virtualenv python-dev
virtualenv ~/.hasalenv            # or "make clean dev-env"
source ~/.hasalenv/bin/activate

pip install selenium

sudo apt-get install wget libav-tools ffmpeg libavc1394-0 libavformat-extra-53 libavfilter2 libavutil-extra-51 mencoder libavahi-common-data xsel xclip
wget https://github.com/bgirard/Gecko-Profiler-Addon/blob/master/geckoprofiler-signed.xpi?raw=true
wget https://github.com/Itseez/opencv/archive/3.0.0.zip
follow this link[http://www.pyimagesearch.com/2015/06/22/install-opencv-3-0-and-python-2-7-on-ubuntu/] to install opencv or:

sudo apt-get install build-essential cmake git pkg-config
sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev
sudo apt-get install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libatlas-base-dev gfortran
sudo pip install virtualenv virtualenvwrapper
sudo apt-get install pip
sudo apt-get install python-pip
sudo apt-get install python2.7-dev
pip install numpy
git clone https://github.com/Itseez/opencv.git
cd opencv
git checkout 3.1.0
cd ..
git clone https://github.com/Itseez/opencv_contrib.git
cd opencv_contrib/
git checkout 3.1.0
cd ../opencv

mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules -D BUILD_EXAMPLES=ON ..
make -j4
sudo make install
sudo ldconfig
ln -s /usr/local/lib/python2.7/site-packages/cv2.so virtualenv_path_you_create/lib/python2.7/site-packages/cv2.so

cd PATH_TO_HASAL
python setup.py install
```

## For Mac OS:

```
virtualenv PATH_TO_YOUR_VENV            # or "make clean dev-env"
source PATH_TO_YOUR_VENV/bin/activate

brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-frei0r --with-libass --with-libvo-aacenc --with-libvorbis --with-libvpx --with-opencore-amr --with-openjpeg --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools
brew install libav
brew tap homebrew/science
brew install opencv
ln -s /usr/local//Cellar/opencv/2.4.13/lib/python2.7/site-packages/cv2.so PATH_TO_YOUR_VENV/lib/python2.7/site-packages/cv2.so

cd PATH_TO_HASAL
python setup.py install
```

OR manual build opencv2
```
virtualenv PATH_TO_YOUR_VENV           # or "make clean dev-env"
source PATH_TO_YOUR_VENV/bin/activate

download the opencv2 package, compile and install
download the opencv2 package here : https://github.com/Itseez/opencv/archive/2.4.13.zip
  unzip the package 
  cmake the folder unzipped 
  make
  make install
  ln -s /usr/local/lib/python2.7/site-packages/cv2.so PATH_TO_YOUR_VENV/lib/python2.7/site-packages/cv2.so

cd PATH_TO_HASAL
python setup.py install
```

## VM Template
You can download the VM tempalte for Hasal framework environment from vagrant.
* vagrant init shako/hasal
* vagrant up --provider virtualbox
* Default user name and password : hasal/hasal

## Setup

## Usage

### Sample 
* Trigger the framework: `python runtest.py re suite.txt`
* Run only once:         `python runtest.py re suite.txt --max-run=1 --max-retry=1`
* Record the profiler:   `python runtest.py re suite.txt --profiler=justprofiler`
* Run with proxy:        `python runtest.py re suite.txt --profiler=avconv,mitmdump`

### Usage
```
  runtest.py re <suite.txt> [--online] [--online-config=<str>] [--max-run=<int>] [--max-retry=<int>] [--keep-browser] [--calc-si] [--profiler=<str>] [--comment=<str>] [--advance]
  runtest.py pt <suite.txt> [--online] [--online-config=<str>] [--max-run=<int>] [--max-retry=<int>] [--keep-browser] [--calc-si] [--profiler=<str>] [--comment=<str>] [--advance]
  runtest.py (-h | --help)
```

### Options:
```
  -h --help                 Show this screen.
  --max-run=<int>           Test run max no [default: 30].
  --max-retry=<int>         Test failed retry max no [default: 15].
  --keep-browser            Keep the browser open after test script executed
  --calc-si                 Calculate the speed index (si) and perceptual speed index (psi)
  --profiler=<str>          Enabled profiler, current support profiler:avconv,geckoprofiler,harexport,chrometracing,fxall,justprofiler,mitmdump,fxtracelogger [default: avconv]
  --online                  Result will be transfer to server, calculated by server
  --online-config=<str>     Online server config [default: svrConfig.json]
  --comment=<str>           Tag the comment on this test [default: <today>]
  --advance                 Only for expert user
```

### Output folder structure as below:
* `/output/images/sample/[case_class_name]_[timestamp]`: sample images capture before or after execution steps
* `/output/images/output/[case_class_name]_[timestamp]`: images converted from desktop recording video 
* `/output/videos`: video recording during case execution
* `/output/profiles`: profile recording during case execution
* * `.bin`: the Geckon profile recording, can be viewed on https://cleopatra.io/
 
#### suite file template
* regression test case format
* `test_script_path, pre_run_sikuli_script_path, post_run_sikuli_script_path`
* example:
`tests.regression.gdoc.test_firefox_gdoc_read_basic_txt_1,regression/gdoc/common/test_firefox_switchcontentwindow`

* pilot test case format
* `test_sikuli_script_path, pre_run_sikuli_script_path, post_run_sikuli_script_path`
* example:
`tests/pilot/facebook/test_firefox_facebook_load_homepage.sikuli/`
