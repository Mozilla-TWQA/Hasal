# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import common
import basecase
import gdoc

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        com = common.General()
        chrome = browser.Chrome()
        gd = gdoc.gDoc()

        chrome.clickBar()
        chrome.enterLink(self.INPUT_TEST_TARGET)
        sleep(5)
        gd.wait_for_loaded()

        setAutoWaitTimeout(10)
        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample2_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME.replace('sample_1', 'sample_2'))
        os.remove(sample1_fp)

        sleep(2)
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        t1 = time.time()
        capimg1 = capture(0, 0, capture_width, capture_height)
        wheel(Pattern("pics/doc_content_left_top_page_region.png").similar(0.85), WHEEL_DOWN, 100)
        sleep(0.2)
        t2 = time.time()
        capimg2 = capture(0, 0, capture_width, capture_height)
        com.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)
        shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
        shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))


case = Case(sys.argv)
case.run()
