from sikuli import *  # NOQA
import common


class Gsearch():
    def __init__(self):
        self.common = common.General()
        self.gsearch_image_header = Pattern("pics/gsearch_image_header.png")
        self.gsearch_homepage_buttons = Pattern("pics/gsearch_homepage_buttons.png")

    def wait_gsearch_loaded(self):
        wait(self.gsearch_homepage_buttons, 15)

    def wait_gimage_loaded(self):
        wait(self.gsearch_image_header, 15)

    def focus_search_inputbox(self):
        click(self.gsearch_homepage_buttons.targetOffset(-7, -71))

    # click the image located in xth row and yth column (1 based)
    # for example, the very first image is (1,1).
    # this calculation is based on english version of google image search only
    def click_result_image(self, x, y):
        a = -120 + 280 * (x - 1)
        b = 275 + 200 * (y - 1)
        click(self.gsearch_image_header.targetOffset(a, b))

    def hover_result_image(self, x, y):
        a = -120 + 280 * (x - 1)
        b = 275 + 200 * (y - 1)
        hover(self.gsearch_image_header.targetOffset(a, b))
