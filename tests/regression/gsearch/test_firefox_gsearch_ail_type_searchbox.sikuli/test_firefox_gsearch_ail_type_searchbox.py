# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import basecase
import gsearch

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        self.common.infolog_enable(False)
        self.common.set_mouse_delay(0)

        # Prepare
        gs = gsearch.Gsearch()
        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample1_fp = sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png')
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        # Launch browser
        ff = browser.Firefox()

        # Access link and wait
        ff.clickBar()
        ff.enterLink(self.INPUT_TEST_TARGET)
        pattern, obj = gs.wait_gsearch_loaded()

        # Wait for stable
        sleep(2)

        # PRE ACTIONS
        gs.focus_search_inputbox()

        # Customized Region
        customized_region_name = 'end'

        # part region of search suggestion list
        compare_area = self.tuning_region(obj, x_offset=-140, y_offset=-70, w_offset=200)
        self.set_override_region_settings(customized_region_name, compare_area)

        # Record T1, and capture the snapshot image
        # Input Latency Action
        screenshot, t1 = gs.il_type('a', capture_width, capture_height)

        # In normal condition, a should appear within 100ms,
        # but if lag happened, that could lead the show up after 100 ms,
        # and that will cause the calculation of AIL much smaller than expected.
        sleep(0.1)

        # Record T2
        t2 = time.time()

        # POST ACTIONS
        sleep(2)

        # Write timestamp
        self.common.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)

        # Write the snapshot image
        shutil.move(screenshot, sample1_fp)


case = Case(sys.argv)
case.run()
