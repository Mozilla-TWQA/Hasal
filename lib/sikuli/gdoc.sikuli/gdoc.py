from sikuli import *


class gDoc():
    def __init__(self):
        self.os = str(Settings.getOS())
        self.os_version = str(Settings.getOSVersion())

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

        if self.os.startswith("M"):
            self.alt = Key.CMD
        else:
            self.alt = Key.ALT

    def wait_for_loaded(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        wait(Pattern("pics/gdoc.png").similar(0.85))
        wait(3)
        setAutoWaitTimeout(default_timeout)

    def insert_image_by_url(self, image_url):
        type("i", self.alt)
        type("i", self.alt)
        wait(Pattern("pics/insert_img_identifier.png").similar(0.85))

    # Prevent cursor twinkling on screen
    def deFoucsContentWindow(self):
        wait(Pattern("pics/defoucs_content_window.png").similar(0.85))
        click(Pattern("pics/defoucs_content_window.png").similar(0.85).targetOffset(0, 25))
