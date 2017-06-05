# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import facebook

com = common.General()
ff = browser.Firefox()
fb = facebook.facebook()

ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
fb.wait_for_loaded()
wheel(fb.blue_bar, WHEEL_DOWN, 20)
for i in range(10):
    if fb._exists(fb.FACEBOOK_FEED_END_REMINDER):
        break
    else:
        if i == 9:
            exit(1)
        else:
            wheel(fb.blue_bar, WHEEL_DOWN, 20)
