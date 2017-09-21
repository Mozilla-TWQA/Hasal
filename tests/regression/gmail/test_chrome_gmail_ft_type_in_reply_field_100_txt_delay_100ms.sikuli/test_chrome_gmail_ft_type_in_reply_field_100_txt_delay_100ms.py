# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import os
import basecase
import gmail

import shutil
import browser
import time


class Case(basecase.SikuliInputLatencyCase):

    def run(self):
        # Disable Sikuli action and info log
        self.common.infolog_enable(False)
        Settings.MoveMouseDelay = 0
        delay = self.common.find_key_type_delay()

        # Prepare
        app = gmail.gMail()
        sample1_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME)
        sample2_fp = os.path.join(self.INPUT_IMG_SAMPLE_DIR_PATH, self.INPUT_IMG_OUTPUT_SAMPLE_1_NAME.replace('sample_1', 'sample_2'))
        capture_width = int(self.INPUT_RECORD_WIDTH)
        capture_height = int(self.INPUT_RECORD_HEIGHT)

        # Launch browser
        my_browser = browser.Chrome()

        # Access link and wait
        my_browser.clickBar()
        my_browser.enterLink(self.INPUT_TEST_TARGET)
        app.wait_for_loaded()

        # Wait for stable
        sleep(2)

        # PRE ACTIONS
        app.click_first_mail()
        sleep(2)
        app.click_reply_btn()
        sleep(2)

        # Customized Region
        customized_region_name_start = 'start'
        customized_region_name_end = 'end'

        # part region of search suggestion list
        _, reply_btn_region = app.wait_for_component_display(app.GMAIL_TYPE_FOR_REPLY, similarity=0.8)
        compare_area = self.tuning_region(reply_btn_region, x_offset=-10, y_offset=30, w_offset=650, h_offset=15)
        self.set_override_region_settings(customized_region_name_start, compare_area)
        self.set_override_region_settings(customized_region_name_end, compare_area)

        t1 = time.time()
        capimg1 = capture(0, 0, capture_width, capture_height)
        char_str = "orempsumdorstametconsecteturadpscngetsedoeusmodtem\nporncduntutaboretdoremagnaquatenmadmnvenamqusnoex"

        self.common.system_print('Type char')
        self.common.delayed_type(char_str, 0.1, delay)

        sleep(1)
        t2 = time.time()
        capimg2 = capture(0, 0, capture_width, capture_height)
        self.common.updateJson({'t1': t1, 't2': t2}, self.INPUT_TIMESTAMP_FILE_PATH)
        shutil.move(capimg1, sample1_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))
        shutil.move(capimg2, sample2_fp.replace(os.path.splitext(sample1_fp)[1], '.png'))

        # POST ACTIONS
        sleep(2)
        app.click_reply_del_btn()


case = Case(sys.argv)
case.run()
