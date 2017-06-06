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
setAutoWaitTimeout(10)
fb.wait_for_loaded()
click(fb.club_post_marker.targetOffset(55, 75))
fb._click(component=fb.FACEBOOK_CLUB_POST_MENU_DELETE)
sleep(1)
click(fb.club_delete_post_button)
wait(fb.club_post_area)
