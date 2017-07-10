# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import facebook

com = common.General()
chrome = browser.Chrome()
fb = facebook.facebook()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

sleep(2)
fb.wait_for_loaded()
fb.focus_window()
count = 0
while not fb.exists(fb.FACEBOOK_ACTIVITY_END_REMINDER, timeout=0.3):
    sleep(0.3)
    type(Key.PAGE_DOWN)
    sleep(0.3)
    type(Key.PAGE_DOWN)
    sleep(0.3)
    type(Key.PAGE_DOWN)
    count += 1
    if count >= 30:
        exit(1)
