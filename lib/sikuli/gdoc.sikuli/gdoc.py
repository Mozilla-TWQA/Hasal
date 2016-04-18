from sikuli import *


class gDoc():
    def __init__(self):
        self.os = str(Settings.getOS())
        self.os_version = str(Settings.getOSVersion())

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

    def wait_for_loaded(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        wait(Pattern("pics/gdoc.png").similar(0.85))
        wait(3)
        setAutoWaitTimeout(default_timeout)

    # Prevent cursor twinkling on screen
    def deFoucsContentWindow(self):
        wait(Pattern("pics/defoucs_content_window.png").similar(0.85))
        click(Pattern("pics/defoucs_content_window.png").similar(0.85).targetOffset(0, 25))

    def create_table(self, row_no, col_no):
        wait(Pattern("pics/toolbar_insert.png").similar(0.85))
        type("i", self.alt + Key.SHIFT)
        wait(Pattern("pics/toolbar_insert_table.png").similar(0.55))
        type("t")
        wait(Pattern("pics/toolbar_insert_table_grid.png").similar(0.55))
        for col_index in range(1, col_no):
            type(Key.RIGHT)
        for row_index in range(1, row_no):
            type(Key.DOWN)
        type(Key.ENTER)


