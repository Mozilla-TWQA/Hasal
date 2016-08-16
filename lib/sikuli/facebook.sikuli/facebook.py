from sikuli import *
import sys
import common


class facebook():
    def __init__(self):
        self.common = common.General()

        if sys.platform == 'darwin':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

    def wait_for_loaded(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        wait(Pattern("pics/facebook_logo.png").similar(0.85), 10)
        setAutoWaitTimeout(default_timeout)
        self.focus_window()

    def focus_window(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        click(Pattern("pics/facebook_logo.png").similar(0.85).targetOffset(0,15))
        setAutoWaitTimeout(default_timeout)

    def post_url(self):
        self.click_home_post_area()
        paste('https://en.wikipedia.org/wiki/Sun_Tzu ')
        wait("pics/facebook_post_url_thumbnail.png", 10)
        wait(1)
        click(Pattern("pics/facebook_post_button.png").similar(0.85))
        wait(Pattern("pics/facebook_post_url_result.png").similar(0.85), 10)
        print('[Facebook] post_url() done.')

    def post_url_del(self):
        wait(Pattern("pics/facebook_post_url_result.png").similar(0.85), 10)
        click(Pattern("pics/facebook_post_url_result.png").similar(0.85).targetOffset(230,-200))
        wait(Pattern("pics/facebook_delete_post_menu.png").similar(0.60), 10)
        click(Pattern("pics/facebook_delete_post_menu.png").targetOffset(0,-10))
        wait(Pattern("pics/facebook_delete_post_button.png").similar(0.85), 10)
        click(Pattern("pics/facebook_delete_post_button.png").similar(0.85).targetOffset(30,0))
        waitVanish(Pattern("pics/facebook_delete_post_button.png").similar(0.85), 10)
        waitVanish(Pattern("pics/facebook_post_url_result.png").similar(0.85), 10)
        print('[Facebook] post_url_del() done.')

    def click_home_post_area(self):
        click(Pattern("pics/facebook_home_post_area.png").similar(0.85))
        wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))

    def click_club_post_area(self):
        click(Pattern("pics/facebook_club_post_area.png").similar(0.85).targetOffset(0,15))
        wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))

    def click_personal_post_area(self):
        click(Pattern("pics/facebook_personal_post_area.png").similar(0.85))
        wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))
