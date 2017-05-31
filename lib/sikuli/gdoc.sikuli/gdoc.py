import os
from sikuli import *  # NOQA
from common import WebApp


class gDoc(WebApp):
    """
            The GDoc library for Sikuli cases.
            The component structure:
                <COMPONENT-NAME> = [
                    [<COMPONENT-IMAGE-PLATFORM-FOO>, <OFFSET-X>, <OFFSET-Y>],
                    [<COMPONENT-IMAGE-PLATFORM-BAR>, <OFFSET-X>, <OFFSET-Y>]
                ]
    """

    GDOC_FAVORITE_ICON = [
        [os.path.join('pics', 'gdoc.png'), 0, 0]
    ]

    GDOC_PRINTER_ICON = [
        [os.path.join('pics', 'printer.png'), 0, 0]
    ]

    GDOC_FOCUS_CONTENT = [
        [os.path.join('pics', 'printer.png'), 50, 60]
    ]

    GDOC_DEFOCUS_CONTENT_IMAGE = [
        [os.path.join('pics', 'defocus_content_window.png'), 0, 0]
    ]

    GDOC_DEFOCUS_CONTENT = [
        [os.path.join('pics', 'defocus_content_window.png'), 0, 25]
    ]

    GDOC_TOOLBAR_INSERT = [
        [os.path.join('pics', 'toolbar_insert.png'), 0, 0]
    ]

    GDOC_TOOLBAR_INSERT_TABLE = [
        [os.path.join('pics', 'toolbar_insert_table.png'), 0, 0]
    ]

    GDOC_TOOLBAR_INSERT_TABLE_GRID = [
        [os.path.join('pics', 'toolbar_insert_table_grid.png'), 0, 0]
    ]

    GDOC_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON = [
        [os.path.join('pics', 'toolbar_insert_image_db_urlbar.png'), 0, 0]
    ]

    GDOC_CLICK_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON = [
        [os.path.join('pics', 'toolbar_insert_image_db_urlbar.png'), 100, 0]
    ]

    GDOC_TOOLBAR_INSERT_IMAGE_DB = [
        [os.path.join('pics', 'toolbar_insert_image_db.png'), 0, 0]
    ]

    GDOC_CLICK_TOOLBAR_INSERT_IMAGE_DB_URL = [
        [os.path.join('pics', 'toolbar_insert_image_db.png'), 100, 0]
    ]

    GDOC_FINDANDPLACE_IMAGE = [
        [os.path.join('pics', 'FindAndReplace.png'), 0, 0]
    ]

    GDOC_CLICK_FIND_FINDANDPLACE_INPUT = [
        [os.path.join('pics', 'FindReplaceInput.png'), 98, -21]
    ]

    GDOC_CLICK_REPLACE_FINDANDPLACE_INPUT = [
        [os.path.join('pics', 'FindReplaceInput.png'), 98, 26]
    ]

    GDOC_REPLACE_ICON = [
        [os.path.join('pics', 'Replace.png'), 0, 0]
    ]

    GDOC_URL_CHECKED = [
        [os.path.join('pics', 'url_checked.png'), 0, 0]
    ]

    GDOC_CONTENT_LEFT_TOP_PAGE_REGION = [
        [os.path.join('pics', 'doc_content_left_top_page_region.png'), 0, 0]
    ]

    def wait_for_loaded(self, similarity=0.85):
        return self._wait_for_loaded(component=gDoc.GDOC_FAVORITE_ICON, similarity=similarity, timeout=60)
        wait(3)
        self.focus_content()

    def focus_content(self, similarity=0.60):
        self._wait_for_loaded(component=gDoc.GDOC_PRINTER_ICON, similarity=similarity, timeout=60)
        self._click(action_name='Focus content', component=gDoc.GDOC_FOCUS_CONTENT)
        wait(3)

    # Prevent cursor twinkling on screen
    def deFoucsContentWindow(self, similarity=0.70):
        self._wait_for_loaded(component=gDoc.GDOC_DEFOCUS_CONTENT_IMAGE, similarity=similarity)
        self._click(action_name='Defocus content', component=gDoc.GDOC_DEFOCUS_CONTENT)

    def create_table(self, row_no, col_no):
        self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT, similarity=0.8)
        type("i", self.alt + Key.SHIFT)
        self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT_TABLE, similarity=0.55)
        type("t")
        self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT_TABLE_GRID, similarity=0.55)
        for col_index in range(1, col_no):
            type(Key.RIGHT)
        for row_index in range(1, row_no):
            type(Key.DOWN)
        type(Key.ENTER)

    def insert_image_url(self, img_url):
        self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT, similarity=0.5)
        type("i", self.alt + Key.SHIFT)
        self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT, similarity=0.5)
        type("i")
        for i in range(10):
            sleep(2)
            if self._exists(gDoc.GDOC_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON, similarity=0.6):
                self._click(action_name='Click toolbar insert image db urlbar', similarity=0.6,
                            component=gDoc.GDOC_CLICK_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON)
            else:
                self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT_IMAGE_DB, similarity=0.5)
                self._click(action_name='Click toolbar insert image db url', similarity=0.6,
                            component=gDoc.GDOC_CLICK_TOOLBAR_INSERT_IMAGE_DB_URL)
                sleep(1)
                self._wait_for_loaded(component=gDoc.GDOC_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON, similarity=0.6)
                self._click(action_name='Click toolbar insert image db urlbar', similarity=0.6,
                            component=gDoc.GDOC_CLICK_TOOLBAR_INSERT_IMAGE_DB_URLBAR_ICON)

            self.com.select_all()
            paste(img_url)
            sleep(2)
            self.com.select_all()
            sleep(1)
            self.com.copy()
            sleep(1)
            self.com.paste()
            sleep(2)
            if self._exists(gDoc.GDOC_URL_CHECKED, similarity=0.6):
                type(Key.ENTER)
                break

    def page_text_generate(self, keyword, page):
        # 92*46 is full page, 80*40 to make it faster
        for j in range(page):
            for i in range(60 * 40):
                if i % 60 == 0:
                    type(Key.ENTER)
                num = i % 26
                str = keyword
                if num < str.__len__():
                    type(str[num])
                else:
                    type(chr(97 + num))
            type(Key.ENTER, Key.CTRL)

    def text_replace(self, search_keyword, replace_keyword, replace_times):
        type("h", self.control)
        self._wait_for_loaded(component=gDoc.GDOC_FINDANDPLACE_IMAGE, similarity=0.5)
        self._click(action_name='Click find button', similarity=0.5,
                    component=gDoc.GDOC_CLICK_FIND_FINDANDPLACE_INPUT)
        type(search_keyword)
        self._click(action_name='Click replace button', similarity=0.5,
                    component=gDoc.GDOC_CLICK_REPLACE_FINDANDPLACE_INPUT)
        type(replace_keyword)
        for i in range(replace_times):
            self._wait_for_loaded(component=gDoc.GDOC_REPLACE_ICON, similarity=0.8)
            self._click(action_name='Click replace button', similarity=0.8, component=gDoc.GDOC_REPLACE_ICON)
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

    def move_to_highlight_scroll(self, input_direction, scroll_down_size):
        self._mouseMove(action_name='Mouse move to component', component=gDoc.GDOC_CONTENT_LEFT_TOP_PAGE_REGION,
                        similarity=0.85)
        self._wheel(action_name='Wheel mouse on component', component=gDoc.GDOC_CONTENT_LEFT_TOP_PAGE_REGION,
                    input_direction=input_direction, input_wheel_size=scroll_down_size, similarity=0.85)
