from sikuli import *
import json	

class General():
    def __init__(self):
        self.os = str(Settings.getOS())
        self.os_version = str(Settings.getOSVersion())
        self.project_base = "/".join(getBundleFolder().split("/")[:-3])
        self.json_path = self.project_base + "/output/profiles/"

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    # This will take in an array of key combinations like [[Key.Enter], [Key.ENTER, Key.CTRL], ["8", Key.CTRL+Key.SHIFT]]
    def key_actions(self, array)
        for action in array:
            sleep(0.3)
            type(*action)

    # Use "highlight" or "popup" to make an anchor for current video
    # style == 0: hightlight, input should be image location
    # style == 1: popup, input should be text
    def img_locator(self, inputc, style=1):
        if style == 1:
            popup(inputc)
        elif style == 0:
            find(inputc).highlight(1)

    def dumpToJson(self, data, filename, mode="w+"):
        with open(self.json_path + filename, mode) as f:
            json.dump(data, f, indent=2)

    def copy(self):
        type("c", self.control)

    def cut(self):
        type("x", self.control)

    def paste(self):
        type("v", self.control)

    def capLock(self, lock):
        if lock != Key.isLockOn(Key.CAPS_LOCK):
            type(Key.CAPS_LOCK)

    def select_all(self):
        type("a", self.control)

    def page_end(self):
        type(Key.END, self.control)

    def page_start(self):
        type(Key.HOME, self.control)
