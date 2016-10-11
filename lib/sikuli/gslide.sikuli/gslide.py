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

        self.gslide_logo = Pattern("pics/gslide.png").similar(0.85)

    def wait_for_loaded(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        wait(self.gslide_logo)
        setAutoWaitTimeout(default_timeout)

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
