# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import facebook

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        setAutoWaitTimeout(10)
        com = common.General()
        com.infolog_enable(0)

        ff = browser.Firefox()
        fb = facebook.facebook()

        ff.clickBar()
        ff.enterLink(self.INPUT_TEST_TARGET)
        _, obj = fb.wait_for_loaded()
        sleep(2)

        # Customized Region
        customized_region_name = 'end'

        # part region of search suggestion list
        compare_area = self.tuning_region(obj, x_offset=175, y_offset=35, w_offset=500, h_offset=150)
        self.set_override_region_settings(customized_region_name, compare_area)
        hover(compare_area)

        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        t1 = time.time()
        capimg2 = capture(0, 0, capture_width, capture_height)

        com.system_print('[log]  Scroll 1 Step')
        ff.scroll_down(1)
        sleep(1)
        t2 = time.time()
        com.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)
        shutil.move(capimg2, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))


case = Case(sys.argv)
case.run()
