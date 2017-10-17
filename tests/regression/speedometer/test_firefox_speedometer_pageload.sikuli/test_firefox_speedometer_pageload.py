# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import speedometer

import shutil
import browser
import time


class Case(basecase.SikuliCase):

    def run(self):
        # Disable Sikuli action and info log
        com = common.General()
        com.infolog_enable(False)
        com.set_mouse_delay(0)

        # Prepare
        app = speedometer.speedometer()

        # Launch browser
        my_browser = browser.Firefox()

        # Access link and wait
        my_browser.clickBar()
        my_browser.enterLink(self.INPUT_TEST_TARGET)
        app.wait_for_loaded()

        # Wait for stable
        sleep(2)

        # ACTIONS
        app.start_test()

        # POST ACTIONS
        # wait for test finish
        app.wait_for_test_finish()
        sleep(1)

        # click test result details
        app.click_test_result_details()
        sleep(1)

        # copy detail information to clipboard
        app.copy_detail_information_to_clipboard()


case = Case(sys.argv)
case.run()
