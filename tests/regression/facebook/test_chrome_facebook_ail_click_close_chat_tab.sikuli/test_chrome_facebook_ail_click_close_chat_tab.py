# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import basecase
import facebook

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        self.common.infolog_enable(False)
        self.common.set_mouse_delay(0)

        # Prepare
        app = facebook.facebook()
        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample1_fp = sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png')
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        # Launch browser
        chrome = browser.Chrome()

        # Access link and wait
        chrome.clickBar()
        chrome.enterLink(self.INPUT_TEST_TARGET)
        app.wait_for_loaded()

        # Wait for stable
        sleep(2)

        # PRE ACTIONS
        app.click_right_panel_contact()
        sleep(2)
        pattern, obj = app.wait_for_close_button_loaded()

        # Customized Region
        customized_region_name = 'end'

        # part region of search suggestion list
        compare_area = self.tuning_region(obj, x_offset=-145, w_offset=145, h_offset=305)
        self.set_override_region_settings(customized_region_name, compare_area)

        # Record T1, and capture the snapshot image
        # Input Latency Action
        loc, screenshot, t1 = app.il_click_close_chat_tab(capture_width, capture_height)

        # In normal condition, a should appear within 100ms,
        # but if lag happened, that could lead the show up after 100 ms,
        # and that will cause the calculation of AIL much smaller than expected.
        sleep(0.1)

        # Record T2
        t2 = time.time()

        # POST ACTIONS
        sleep(2)
        app.wait_pattern_for_vanished(pattern=pattern)

        # Write timestamp
        self.common.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)

        # Write the snapshot image
        shutil.move(screenshot, sample1_fp)


case = Case(sys.argv)
case.run()
