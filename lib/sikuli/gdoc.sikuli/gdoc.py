from sikuli import *


class gDoc():
    def __init__(self):
        self.os = Settings.getOS()
        self.os_version = Settings.getOSVersion()

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    def wait_for_loaded(self):
        wait(Pattern("pics/gdoc_star.png").similar(0.85))
        wait(2)

