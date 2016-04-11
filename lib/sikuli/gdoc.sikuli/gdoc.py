from sikuli import *


class gDoc():
    def __init__(self):
        self.os = str(Settings.getOS())
        self.os_version = str(Settings.getOSVersion())

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    def wait_for_loaded(self):
        wait(Pattern("pics/gdoc_star.png").similar(0.85))
        wait(2)

