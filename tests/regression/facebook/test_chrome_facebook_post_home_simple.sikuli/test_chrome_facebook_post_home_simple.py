# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import basecase
import facebook
import browser
import random


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        chrome = browser.Chrome()
        fb = facebook.facebook()

        chrome.clickBar()
        chrome.enterLink(self.INPUT_TEST_TARGET)
        fb.wait_for_loaded()
        sleep(2)

        fb.click_post_area_home()
        type("abcdef" + str(random.randint(1, 100000)))
        type(Key.ENTER, self.common.control)


case = Case(sys.argv)
case.run()
