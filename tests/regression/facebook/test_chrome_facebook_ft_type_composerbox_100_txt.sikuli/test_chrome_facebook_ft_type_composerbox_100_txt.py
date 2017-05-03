# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import os
import common
import string
import facebook
import shutil
import browser
import time

# Disable Sikuli action and info log
com = common.General()
com.infolog_enable(False)

chrome = browser.Chrome()
fb = facebook.facebook()

chrome.clickBar()
chrome.enterLink(sys.argv[3])
fb.wait_for_loaded()

sleep(2)
fb.click_post_area_home()
sample1_fp = os.path.join(sys.argv[4], sys.argv[5])
sample2_fp = os.path.join(sys.argv[4], sys.argv[5].replace('sample_1', 'sample_2'))

sleep(2)
capture_width = int(sys.argv[6])
capture_height = int(sys.argv[7])

com.set_type_delay(0.06)

t1 = time.time()
capimg1 = capture(0, 0, capture_width, capture_height)

char_len = 100
char_str = (string.ascii_lowercase * (char_len / 26 + 1))[:char_len]
com.system_print('Type char')
type(char_str)

sleep(1)
t2 = time.time()
capimg2 = capture(0, 0, capture_width, capture_height)
com.updateJson({'t1': t1, 't2': t2}, sys.argv[8])
shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
