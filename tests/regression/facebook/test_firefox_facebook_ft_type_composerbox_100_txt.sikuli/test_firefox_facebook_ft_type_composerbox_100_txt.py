# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import facebook

import string
import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        com = common.General()
        com.infolog_enable(False)

        ff = browser.Firefox()
        fb = facebook.facebook()

        ff.clickBar()
        ff.enterLink(self.INPUT_TEST_TARGET)
        fb.wait_for_loaded()

        sleep(2)
        fb.click_post_area_home()
        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample2_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME.replace('sample_1', 'sample_2'))

        sleep(2)
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        com.set_type_delay(0.06)

        t1 = time.time()
        capimg1 = capture(0, 0, capture_width, capture_height)

        char_len = 100
        char_str = (string.ascii_lowercase * (char_len / 26 + 1))[:char_len]
        com.system_print('Type char')
        type(char_str)

        sleep(1)
        t2 = time.time()
        capimg2 = capture(0, 0, capture_width, capture_height)
        com.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)
        shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
        shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))


case = Case(sys.argv)
case.run()
