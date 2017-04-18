# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc
import shutil
import time
import os

com = common.General()
ff = browser.Firefox()
gd = gdoc.gDoc()

ff.clickBar()
ff.enterLink(sys.argv[3])
sleep(5)
gd.wait_for_loaded()

setAutoWaitTimeout(10)
sample1_fp = os.path.join(sys.argv[4], sys.argv[5])
sample2_fp = os.path.join(sys.argv[4], sys.argv[5].replace('sample_1', 'sample_2'))

sleep(2)
capture_width = int(sys.argv[6])
capture_height = int(sys.argv[7])

t1 = time.time()
capimg1 = capture(0, 0, capture_width, capture_height)
gd.move_to_highlight_scroll(WHEEL_DOWN, 1)
sleep(1)
t2 = time.time()
capimg2 = capture(0, 0, capture_width, capture_height)
com.updateJson({'t1': t1, 't2': t2}, sys.argv[8])
shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
