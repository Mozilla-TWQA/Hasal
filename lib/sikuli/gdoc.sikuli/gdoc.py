from sikuli import *
import common


class gDoc():
    def __init__(self):
        self.os = str(Settings.getOS())
        self.os_version = str(Settings.getOSVersion())
        self.com = common.General()

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
        wait(Pattern("pics/defocus_content_window.png").similar(0.70))
        click(Pattern("pics/defocus_content_window.png").similar(0.70).targetOffset(0, 25))

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

    def insert_image_url(self, img_url):
        wait(Pattern("pics/toolbar_insert.png"))
        type("i", self.alt + Key.SHIFT)
        wait(Pattern("pics/toolbar_insert_image.png"))
        type("i")
        for i in range(5):
            sleep(2)
            if exists(Pattern("pics/toolbar_insert_image_db_urlbar.png")):
                click(Pattern("pics/toolbar_insert_image_db_urlbar.png").targetOffset(100, 0))
            else:
                wait(Pattern("pics/toolbar_insert_image_db.png"))
                click(Pattern("pics/toolbar_insert_image_db_url.png"))
                sleep(1)
                wait(Pattern("pics/toolbar_insert_image_db_urlbar.png"))
                click(Pattern("pics/toolbar_insert_image_db_urlbar.png").targetOffset(100, 0))

            self.com.select_all()
            type(img_url)
            sleep(2)
            self.com.select_all()
            sleep(1)
            self.com.copy()
            sleep(1)
            self.com.paste()
            sleep(2)

            if exists(Pattern("pics/url_checked.png")):
                type(Key.ENTER)
                break

    def page_text_generate(self, keyword, page):
        #92*46 is full page, 80*40 to make it faster
        for j in range(page):
            for i in range(60*40):
                if (i % 60 == 0):
                    type(Key.ENTER)
                num = i % 26
                str = keyword
                if num < str.__len__():
                    type(str[num])
                else:
                    type(chr(97+num))
            type(Key.ENTER, Key.CTRL)

    def text_replace(self, search_keyword, replace_keyword, replace_times):
        type("h", Key.CTRL)
        wait(Pattern("pics/FindAndReplace.png"))
        click(Pattern("pics/FindReplaceInput.png").targetOffset(98, -21))
        type(search_keyword)
        click(Pattern("pics/FindReplaceInput.png").targetOffset(98, 26))
        type(replace_keyword)
        for i in range(replace_times):
            wait(Pattern("pics/Replace.png").similar(0.90))
            click(Pattern("pics/Replace.png").similar(0.90))
        wait(2)
        type(Key.ESC)

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

    def number_list(self):
        type("7", self.control + Key.SHIFT)

    def bullet_list(self):
        type("8", self.control + Key.SHIFT)

