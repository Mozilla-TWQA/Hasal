from sikuli import *  # NOQA
import os
import sys
import common


class gSlide():
    def __init__(self, type=None):
        self.common = common.General()
        self.os = str(Env.getOS())
        self.type = type

        if self.os.lower() == 'mac':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

        self.default_timeout = getAutoWaitTimeout()
        self.wait_time = 30
        setAutoWaitTimeout(self.wait_time)

        self.folder = os.path.join("pics", self.os.lower(), self.type)
        self.gslide_logo = Pattern(os.path.join(self.folder, "gslide.png")).similar(0.70)
        self.gslide_icon = Pattern(os.path.join(self.folder, "gslide_icon.png")).similar(0.70)
        self.page_end = Pattern(os.path.join(self.folder, "page_end.png")).similar(0.70)
        self.presentation_mode = Pattern(os.path.join(self.folder, "presentation_mode.png")).similar(0.70)
        self.presentation_blank_end = Pattern(os.path.join(self.folder, "presentation_blank_end.png")).similar(0.70)
        self.presentation_page_2 = Pattern(os.path.join(self.folder, "presentation_page_2.png")).similar(0.60)
        self.presentation_page_3 = Pattern(os.path.join(self.folder, "presentation_page_3.png")).similar(0.60)
        self.presentation_page_4 = Pattern(os.path.join(self.folder, "presentation_page_4.png")).similar(0.60)
        self.presentation_page_5 = Pattern(os.path.join(self.folder, "presentation_page_5.png")).similar(0.60)
        self.presentation_page_6 = Pattern(os.path.join(self.folder, "presentation_page_6.png")).similar(0.60)
        self.presentation_page_7 = Pattern(os.path.join(self.folder, "presentation_page_7.png")).similar(0.60)
        self.presentation_page_8 = Pattern(os.path.join(self.folder, "presentation_page_8.png")).similar(0.60)
        self.presentation_page_9 = Pattern(os.path.join(self.folder, "presentation_page_9.png")).similar(0.60)
        self.presentation_page_end = Pattern(os.path.join(self.folder, "presentation_page_end.png")).similar(0.60)
        self.blank_list_original = Pattern(os.path.join(self.folder, "blank_list_original.png")).similar(0.85)
        self.blank_list_final = Pattern(os.path.join(self.folder, "blank_list_final.png")).similar(0.85)
        self.image_chart_list = Pattern(os.path.join(self.folder, "image_chart_list.png")).similar(0.85)
        self.image_chart_list_page_2 = Pattern(os.path.join(self.folder, "image_chart_list_page_2.png")).similar(0.95)
        self.image_chart_list_page_3 = Pattern(os.path.join(self.folder, "image_chart_list_page_3.png")).similar(0.95)
        self.image_chart_list_page_4 = Pattern(os.path.join(self.folder, "image_chart_list_page_4.png")).similar(0.95)
        self.image_chart_list_page_end = Pattern(os.path.join(self.folder, "image_chart_list_page_end.png")).similar(0.95)
        self.animation_list = Pattern(os.path.join(self.folder, "animation_list.png")).similar(0.85)
        self.shape_list = Pattern(os.path.join(self.folder, "shape_list.png")).similar(0.85)
        self.table_list = Pattern(os.path.join(self.folder, "table_list.png")).similar(0.85)
        self.text_list = Pattern(os.path.join(self.folder, "text_list.png")).similar(0.85)
        self.utf8_txt_list = Pattern(os.path.join(self.folder, "utf8_txt_list.png")).similar(0.85)
        self.utf8_txt_list_original = Pattern(os.path.join(self.folder, "utf8_txt_list_original.png")).similar(0.85)
        self.mix_content_30_list_original = Pattern(os.path.join(self.folder, "mix_content_30_list_original.png")).similar(0.85)
        self.mix_content_30_list_final = Pattern(os.path.join(self.folder, "mix_content_30_list_final.png")).similar(0.85)
        self.mix_content_30_list_final_end = Pattern(os.path.join(self.folder, "mix_content_30_list_final_end.png")).similar(0.85)
        self.mix_content_50_list_original = Pattern(os.path.join(self.folder, "mix_content_50_list_original.png")).similar(0.85)
        self.mix_content_50_list_final = Pattern(os.path.join(self.folder, "mix_content_50_list_final.png")).similar(0.85)
        self.slides_5_list_original = Pattern(os.path.join(self.folder, "slides_5_list_original.png")).similar(0.85)
        self.slides_5_list_final = Pattern(os.path.join(self.folder, "slides_5_list_final.png")).similar(0.85)
        self.slides_5_list_final_end = Pattern(os.path.join(self.folder, "slides_5_list_final_end.png")).similar(0.85)
        self.slides_10_list_original = Pattern(os.path.join(self.folder, "slides_10_list_original.png")).similar(0.85)
        self.slides_10_list_final = Pattern(os.path.join(self.folder, "slides_10_list_final.png")).similar(0.85)
        self.list_page_2 = Pattern(os.path.join(self.folder, "list_page_2.png")).similar(0.95)
        self.list_page_3 = Pattern(os.path.join(self.folder, "list_page_3.png")).similar(0.95)
        self.list_page_4 = Pattern(os.path.join(self.folder, "list_page_4.png")).similar(0.95)
        self.list_page_5 = Pattern(os.path.join(self.folder, "list_page_5.png")).similar(0.95)
        self.list_page_6 = Pattern(os.path.join(self.folder, "list_page_6.png")).similar(0.95)
        self.list_page_7 = Pattern(os.path.join(self.folder, "list_page_7.png")).similar(0.95)
        self.list_page_8 = Pattern(os.path.join(self.folder, "list_page_8.png")).similar(0.95)
        self.list_page_9 = Pattern(os.path.join(self.folder, "list_page_9.png")).similar(0.95)
        self.list_page_10 = Pattern(os.path.join(self.folder, "list_page_10.png")).similar(0.95)
        self.blank_theme = Pattern(os.path.join(self.folder, "blank_theme.png")).similar(0.70)
        self.theme_mozilla_tag = Pattern(os.path.join(self.folder, "theme_mozilla_tag.png")).similar(0.85)
        self.theme_mozilla_tag_red = Pattern(os.path.join(self.folder, "theme_mozilla_tag_red.png")).similar(0.85)

    def wait_for_loaded(self):
        wait(self.gslide_logo)
        print "wait for loaded: %s" % str(getAutoWaitTimeout())

    def invoke_presentation_mode(self):
        if self.os.lower() == 'mac':
            type(Key.ENTER, self.control)
        else:
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
