# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import os
import gdoc
import shutil
import browser
import time
import json

chrome = browser.Chrome()
gd = gdoc.gDoc()
chrome.clickBar()
chrome.enterLink(sys.argv[3])
gd.wait_for_loaded()

setAutoWaitTimeout(10)
sample1_fp = os.path.join(sys.argv[4], sys.argv[5])
sample2_fp = os.path.join(sys.argv[4], sys.argv[5].replace('sample_1', 'sample_2'))
os.remove(sample1_fp)

sleep(2)
capture_width = int(sys.argv[6])
capture_height = int(sys.argv[7])

t1 = time.time()
capimg1 = capture(0, 0, capture_width, capture_height)
type('a')
# In normal condition, a should appear within 100ms, but if lag happened, that could lead the show up after 100 ms, and that will cause the calculation of AIL much smaller than expected.
sleep(0.1)
t2 = time.time()
capimg2 = capture(0, 0, capture_width, capture_height)
with open(sys.argv[8], "r+") as fh:
    timestamp = json.load(fh)
    timestamp['t1'] = t1
    timestamp['t2'] = t2
    fh.seek(0)
    fh.write(json.dumps(timestamp))
shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
