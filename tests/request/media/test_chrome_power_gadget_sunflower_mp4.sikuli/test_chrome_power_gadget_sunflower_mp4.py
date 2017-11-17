# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.

INPUT_LIB_PATH = sys.argv[1]
sys.path.append(INPUT_LIB_PATH)

import subprocess

import common
import basecase
import browser


class Case(basecase.SikuliCase):

    def run(self):
        # Disable Sikuli action and info log
        com = common.General()
        com.infolog_enable(False)
        com.set_mouse_delay(0)

        # Prepare
        app = App('IntelPowerGadget')
        if app.isRunning():
            app.close()
            print('Close IntelPowerGadget.')
            sleep(2)

        # Launch browser
        my_browser = browser.Chrome()

        # Start Intel Power Gadget
        subprocess.Popen('"c:\Program Files\Intel\Power Gadget 3.5\IntelPowerGadget.exe"')
        sleep(2)
        subprocess.Popen('"c:\Program Files\Intel\Power Gadget 3.5\IntelPowerGadget.exe" -start')

        # Access link and wait
        my_browser.clickBar()
        my_browser.enterLink(self.INPUT_TEST_TARGET)

        # Wait for stable
        sleep(1)

        # ACTIONS
        """
        Reference file: http://distribution.bbb3d.renderfarming.net/video/mp4/bbb_sunflower_1080p_30fps_normal.mp4
        10 m 35 s
        """
        sleep(10 * 60 + 35)

        # POST ACTIONS
        # wait for test finish
        sleep(5)
        subprocess.Popen('"c:\Program Files\Intel\Power Gadget 3.5\IntelPowerGadget.exe" -stop')
        sleep(2)

        app = App('IntelPowerGadget')
        if app.isRunning():
            app.close()
            print('Close IntelPowerGadget.')
            sleep(2)


case = Case(sys.argv)
case.run()
