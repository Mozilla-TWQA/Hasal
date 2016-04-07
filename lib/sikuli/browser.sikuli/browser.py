from sikuli import *


class GeneralBrowser():
    def enterLink(self, link):
        # Enter the link and open google document
        type(link)
        type(Key.ENTER)


class Chrome(GeneralBrowser):
    # Need further permission in Mac OS X and might not be available in windows
    def launchBrowser(self):
        _chrome = App("Chrome")
        if _chrome.isRunning():
            _chrome.close()
        _chrome.open()

    # Wait for URL bar to appear
    def clickBar(self):
        wait(Pattern("pics/chrome_urlbar.png").similar(0.70))
        click(Pattern("pics/chrome_urlbar.png").similar(0.70).targetOffset(-40, 0))


class Firefox(GeneralBrowser):
    # Need further permission in Mac OS X and might not be available in windows
    # Might not working for Firefox (need alternative launch)
    def launchBrowser(self):
        _ff = App("Firefox")
        if _ff.isRunning():
            _ff.close()
        _ff.open()

    # Wait for URL bar to appear
    def clickBar(self):
        wait(Pattern("pics/ff_urlbar.png").similar(0.70))
        click(Pattern("pics/ff_urlbar.png").similar(0.70).targetOffset(-100, 0))
