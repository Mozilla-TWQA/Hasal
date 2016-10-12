from sikuli import *  # NOQA
import sys
import common


class gSlide():
    def __init__(self):
        self.common = common.General()

        if sys.platform == 'darwin':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

        self.default_timeout = getAutoWaitTimeout()
        self.wait_time = 15
        setAutoWaitTimeout(self.wait_time)

        self.gslide_logo = Pattern("pics/gslide.png").similar(0.70)
        self.presentation_mode = Pattern("pics/presentation_mode.png").similar(0.70)
        self.presentation_blank_end = Pattern("pics/presentation_blank_end.png").similar(0.70)
        self.page_2 = Pattern("pics/page_2.png").similar(0.70)
        self.page_3 = Pattern("pics/page_3.png").similar(0.70)
        self.page_4 = Pattern("pics/page_4.png").similar(0.70)
        self.page_5 = Pattern("pics/page_5.png").similar(0.70)
        self.page_6 = Pattern("pics/page_6.png").similar(0.70)
        self.page_7 = Pattern("pics/page_7.png").similar(0.70)
        self.page_8 = Pattern("pics/page_8.png").similar(0.70)
        self.page_9 = Pattern("pics/page_9.png").similar(0.70)
        self.page_end = Pattern("pics/page_end.png").similar(0.70)
        self.presentation_page_2 = Pattern("pics/presentation_page_2.png").similar(0.70)
        self.presentation_page_3 = Pattern("pics/presentation_page_3.png").similar(0.70)
        self.presentation_page_4 = Pattern("pics/presentation_page_4.png").similar(0.70)
        self.presentation_page_5 = Pattern("pics/presentation_page_5.png").similar(0.70)
        self.presentation_page_6 = Pattern("pics/presentation_page_6.png").similar(0.70)
        self.presentation_page_7 = Pattern("pics/presentation_page_7.png").similar(0.70)
        self.presentation_page_8 = Pattern("pics/presentation_page_8.png").similar(0.70)
        self.presentation_page_9 = Pattern("pics/presentation_page_9.png").similar(0.70)
        self.presentation_page_end = Pattern("pics/presentation_page_end.png").similar(0.70)

    def wait_for_loaded(self):
        wait(self.gslide_logo)
        print "wait for loaded: %s" % str(getAutoWaitTimeout())

    def invoke_presentation_mode(self):
        type(Key.F5, self.control)

    def undo(self):
        type("z", self.control)

    def redo(self):
        type("y", self.control)

    def bold(self):
        type("b", self.control)

    def underline(self):
        type("u", self.control)

    def italic(self):
        type("i", self.control)
