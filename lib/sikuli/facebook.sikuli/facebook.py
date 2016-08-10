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
        wait(Pattern("1470820258980.png").similar(0.85), 10)
        setAutoWaitTimeout(default_timeout)
        self.focus_window()

    def focus_window(self):
        default_timeout = getAutoWaitTimeout()
        setAutoWaitTimeout(10)
        click(Pattern("1470820258980.png").similar(0.85).targetOffset(0,15))
        setAutoWaitTimeout(default_timeout)

    def post_url(self):
        click(Pattern("1470818721451.png").similar(0.85))
        paste('https://en.wikipedia.org/wiki/Sun_Tzu ')
        wait("1470822122151.png", 10)
        click(Pattern("1470818889053.png").similar(0.85))
        wait(Pattern("1470821414750.png").similar(0.85), 10)
        print('[Facebook] post_url() done.')

    def post_url_del(self):
        wait(Pattern("1470821414750.png").similar(0.85), 10)
        click(Pattern("1470821414750.png").similar(0.85).targetOffset(230,-200))
        wait(Pattern("1470822426794.png").similar(0.85), 10)
        click(Pattern("1470822426794.png").similar(0.85).targetOffset(-70,-70))
        wait(Pattern("1470821690209.png").similar(0.85), 10)
        click(Pattern("1470821690209.png").similar(0.85).targetOffset(160,50))
        waitVanish(Pattern("1470821690209.png").similar(0.85), 10)
        waitVanish(Pattern("1470821414750.png").similar(0.85), 10)
        print('[Facebook] post_url_del() done.')


my_fb = facebook()
my_fb.wait_for_loaded()

# Post URL
my_fb.post_url()
# Delete posted URL after testing
my_fb.post_url_del()
