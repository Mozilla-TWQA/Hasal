import os
import shutil
import urllib2
import zipfile
from distutils.dir_util import copy_tree

def remove_folder(path):
    # check if folder exists
    if os.path.exists(path):
        print "Removing " + path
        # remove if exists
        shutil.rmtree(path)

def download_nightly():
    url = "https://ftp.mozilla.org/pub/firefox/nightly/latest-mozilla-central/firefox-57.0a1.en-US.win64.zip"

    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"Downloading Firefox Nightly %10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    print "\n"

def unzip_file(file_name):
    print "Extracting " + file_name
    zip_ref = zipfile.ZipFile(file_name, 'r')
    zip_ref.extractall("firefox/")
    zip_ref.close()

def copy_folder(from_folder, to_folder):
    print "Copy from " + from_folder + " to " + to_folder
    copy_tree("firefox/firefox/", "C:\\Program Files (x86)\\Mozilla Firefox\\")

download_nightly()
remove_folder("firefox/")
unzip_file("firefox-57.0a1.en-US.win64.zip")
remove_folder("C:\\Program Files (x86)\\Mozilla Firefox\\")
copy_folder("firefox/firefox/", "C:\\Program Files (x86)\\Mozilla Firefox\\")