# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import os
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
sampleImg1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "content", "sample_1.jpg")
fb.post_content(location='club', content_type='photo_video', input_string=sampleImg1)
