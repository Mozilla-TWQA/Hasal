# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import gdoc
import browser
import basecase


class Case(basecase.SikuliRunTimeCase):

    def run(self):
        # Disable Sikuli action and info log
        ff = browser.Firefox()
        gd = gdoc.gDoc()

        ff.clickBar()
        ff.enterLink(self.INPUT_TEST_TARGET)
        sleep(5)
        gd.wait_for_loaded()

        gd.deFoucsContentWindow()

case = Case(sys.argv)
case.run()
