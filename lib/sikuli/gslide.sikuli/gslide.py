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
        self.gslide_icon = Pattern("pics/gslide_icon.png").similar(0.70)
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
        self.presentation_page_2 = Pattern("pics/presentation_page_2.png").similar(0.60)
        self.presentation_page_3 = Pattern("pics/presentation_page_3.png").similar(0.60)
        self.presentation_page_4 = Pattern("pics/presentation_page_4.png").similar(0.60)
        self.presentation_page_5 = Pattern("pics/presentation_page_5.png").similar(0.60)
        self.presentation_page_6 = Pattern("pics/presentation_page_6.png").similar(0.60)
        self.presentation_page_7 = Pattern("pics/presentation_page_7.png").similar(0.60)
        self.presentation_page_8 = Pattern("pics/presentation_page_8.png").similar(0.60)
        self.presentation_page_9 = Pattern("pics/presentation_page_9.png").similar(0.60)
        self.presentation_page_end = Pattern("pics/presentation_page_end.png").similar(0.60)
        self.blank_list_original = Pattern("pics/blank_list_original.png").similar(0.60)
        self.blank_list_final = Pattern("pics/blank_list_final.png").similar(0.60)
        self.image_chart_list = Pattern("pics/image_chart_list.png").similar(0.70)
        self.shape_list = Pattern("pics/shape_list.png").similar(0.70)
        self.table_list = Pattern("pics/table_list.png").similar(0.70)
        self.text_list = Pattern("pics/text_list.png").similar(0.50)
        self.mix_content_30_list_original = Pattern("pics/mix_content_30_list_original.png").similar(0.60)
        self.mix_content_30_list_final = Pattern("pics/mix_content_30_list_final.png").similar(0.65)
        self.mix_content_30_list_final_end = Pattern("pics/mix_content_30_list_final_end.png").similar(0.85)
        self.utf8_txt_list = Pattern("pics/utf8_txt_list.png").similar(0.50)
        self.slides_5_list_original = Pattern("pics/slides_5_list_original.png").similar(0.70)
        self.slides_5_list_final = Pattern("pics/slides_5_list_final.png").similar(0.70)
        self.slides_5_list_final_end = Pattern("pics/slides_5_list_final_end.png").similar(0.74)
        self.blank_theme = Pattern("pics/blank_theme.png").similar(0.70)
        self.theme_mozilla_tag = Pattern("pics/theme_mozilla_tag.png").similar(0.70)
        self.theme_mozilla_tag_red = Pattern("pics/theme_mozilla_tag_red.png").similar(0.70)

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

    def select_all(self):
        type("a", self.control)

    def invoke_theme_list(self):
        theme_index = 6
        wait(self.gslide_icon)
        sleep(1)
        click(self.gslide_icon.targetOffset(220, 15))
        for i in range(theme_index):
            sleep(0.5)
            type(Key.DOWN)
        type(Key.ENTER)

    def invoke_layout_list(self):
        theme_index = 5
        wait(self.gslide_icon)
        sleep(1)
        click(self.gslide_icon.targetOffset(220, 15))
        for i in range(theme_index):
            sleep(0.5)
            type(Key.DOWN)
        type(Key.RIGHT)
