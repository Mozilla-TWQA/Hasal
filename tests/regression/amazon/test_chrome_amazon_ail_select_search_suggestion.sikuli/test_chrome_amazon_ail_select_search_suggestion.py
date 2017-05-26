# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import amazon

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        com = common.General()
        com.infolog_enable(False)
        com.set_mouse_delay(0)

        # Prepare
        app = amazon.Amazon()
        sample2_file_path = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH,
                                         self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME.replace('sample_1', 'sample_2'))
        sample2_file_path = sample2_file_path.replace(os.path.splitext(sample2_file_path)[1], '.png')
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        # Launch browser
        my_browser = browser.Chrome()

        # Access link and wait
        my_browser.clickBar()
        my_browser.enterLink(self.INPUT_TEST_TARGET)
        pattern = app.wait_for_loaded()

        # Wait for stable
        sleep(2)

        # PRE ACTIONS
        app.click_search_field()
        sleep(1)
        type('m')
        app.wait_pattern_for_vanished(pattern=pattern)
        com.loop_type_key(Key.DOWN, 2, 0.5)

        # Record T1, and capture the snapshot image
        # Input Latency Action
        screenshot, t1 = app.il_type_key_down_search_suggestion(capture_width, capture_height)

        # In normal condition, a should appear within 100ms,
        # but if lag happened, that could lead the show up after 100 ms,
        # and that will cause the calculation of AIL much smaller than expected.
        sleep(0.1)

        # Record T2
        t2 = time.time()

        # POST ACTIONS
        sleep(1)

        # Write timestamp
        com.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)

        # Write the snapshot image
        shutil.move(screenshot, sample2_file_path)


case = Case(sys.argv)
case.run()
