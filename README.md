Google Doc Performance Test
===========================
A Framework for testing Google Doc performance on Firefox

# Installation
* Install Firefox
* Install Selenium for Python
* Install video recording codes and libs
* Install video recording main program
* Install opencv

```
virtualenv venv
source venv/bin/activate

pip install selenium
For Ubuntu:
sudo apt-get install wget libav-tools ffmpeg libavc1394-0 libavformat-extra-53 libavfilter2 libavutil-extra-51 mencoder libavahi-common-data

For Mac OS:
brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-frei0r --with-libass --with-libvo-aacenc --with-libvorbis --with-libvpx --with-opencore-amr --with-openjpeg --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools
brew install libav

wget https://github.com/bgirard/Gecko-Profiler-Addon/blob/master/geckoprofiler-signed.xpi?raw=true

wget https://github.com/Itseez/opencv/archive/3.0.0.zip

follow this link[http://www.pyimagesearch.com/2015/06/22/install-opencv-3-0-and-python-2-7-on-ubuntu/] to install the opencv
```

# Setup 
* Create a google doc, share it to the public (don't require login)
* Copy the link and paste it to `self.docUrl` in `testperf::setUp`

# Usage

```
python -m unittest tests.test_googledoc_sample
```


Output folder structure as below:
* `/output/images/sample/[case_class_name]_[timestamp]`: sample images capture before or after execution steps
* `/output/images/output/[case_class_name]_[timestamp]`: images converted from desktop recording video 
* `/output/videos`: video recording during case execution
* `/output/profiles`: profile recording during case execution
* * `.bin`: the Geckon profile recording, can be viewed on https://cleopatra.io/
