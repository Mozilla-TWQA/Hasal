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
fb._wait(component=fb.FACEBOOK_CLUB_POST_HEADER)
fb._doubleclick(component=facebook.FACEBOOK_CLICK_CLUB_POST_HEADER)
mouseMove(Location(0, 0))
fb.wait_post_area_vanish(location='club')
fb._wait(component=fb.FACEBOOK_VIDEO_STOP_ICON, timeout=240)
