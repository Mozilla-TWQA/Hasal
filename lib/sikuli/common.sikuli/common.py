from sikuli import *


class General():
    def __init__(self):
        self.os = Settings.getOS()
        self.os_version = Settings.getOSVersion()

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    # Use "highlight" or "popup" to make an anchor for current video
    # style == 0: hightlight, input should be image location
    # style == 1: popup, input should be text
    def img_locator(self, inputc, style=1):
        if style == 1:
            popup(inputc)
        elif style == 0:
            find(inputc).highlight(1)

    def copy(self):
        type("c", self.control)

    def cut(self):
        type("x", self.control)

    def paste(self):
        type("p", self.control)

    def capLock(self, lock):
        if lock != Key.isLockOn(Key.CAPS_LOCK):
            type(Key.CAPS_LOCK)
