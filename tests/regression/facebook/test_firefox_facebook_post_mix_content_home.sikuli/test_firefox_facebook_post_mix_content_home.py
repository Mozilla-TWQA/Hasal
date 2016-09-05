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
fb.post_content(location='home', content_type='text',
                input_string='https://en.wikipedia.org/wiki/Sun_Tzu  All warfare is based on deception. Hence, when we '
                             'are able to attack, we must seem unable; when using our forces, we must appear inactive; '
                             'when we are near, we must make the enemy believe we are far away; when far away, we must '
                             'make him believe we are near.')
