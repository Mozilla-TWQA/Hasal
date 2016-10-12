from sikuli import *  # NOQA
import sys
import common


class gSheet():
    def __init__(self):
        self.common = common.General()

        if sys.platform == 'darwin':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

        self.gsheet_tab_icon = Pattern("pics/gsheet.png").similar(0.70)

    def wait_for_loaded(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        wait(self.gsheet_tab_icon)
        setAutoWaitTimeout(default_timeout)

