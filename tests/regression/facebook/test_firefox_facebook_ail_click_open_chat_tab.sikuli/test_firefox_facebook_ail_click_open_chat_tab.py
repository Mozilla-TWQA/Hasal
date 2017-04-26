# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import os
import common
import facebook
import shutil
import browser
import time

# Disable Sikuli action and info log
com = common.General()
com.infolog_enable(0)

ff = browser.Firefox()
fb = facebook.facebook()

ff.clickBar()
ff.enterLink(sys.argv[3])
fb.wait_for_loaded()

sleep(2)
setAutoWaitTimeout(10)

sample2_fp = os.path.join(sys.argv[4], sys.argv[5].replace('sample_1', 'sample_2'))

sleep(5)
capture_width = int(sys.argv[6])
capture_height = int(sys.argv[7])

# Set mouse move delay time to 0 for immediately action requirement
Settings.MoveMouseDelay = 0
hover(fb.right_panel_contact.targetOffset(0, 15))
mouseDown(Button.LEFT)
capimg2 = capture(0, 0, capture_width, capture_height)
t1 = time.time()

print '[log] Mouse Click - Button Up'
mouseUp(Button.LEFT)
mouseMove(fb.right_panel_contact.targetOffset(0, 50))
sleep(0.1)
t2 = time.time()
com.updateJson({'t1': t1, 't2': t2}, sys.argv[8])
shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample2_fp)[1], '.png'))
click(fb.chat_tab_close_button)
if not waitVanish(fb.chat_tab_close_button):
    exit(1)
