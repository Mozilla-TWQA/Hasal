import re
import subprocess
from sikuli import *  # NOQA


class GeneralBrowser():
    def __init__(self):
        self.os = str(Env.getOS())  # Using Env because of sikuli issue from https://bugs.launchpad.net/sikuli/+bug/1514007
        self.os_version = str(Env.getOSVersion())

        if self.os.startswith("M"):
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    def enterLink(self, link):
        paste(link)
        type(Key.ENTER)

    def scroll_down(self, step):
        if self.os.lower() == 'mac':
            wheel(WHEEL_UP, step)
        else:
            # 'windows' and 'linux'
            wheel(WHEEL_DOWN, step)

    def scroll_up(self, step):
        if self.os.lower() == 'mac':
            wheel(WHEEL_DOWN, step)
        else:
            # 'windows' and 'linux'
            wheel(WHEEL_UP, step)


class Chrome(GeneralBrowser):
    def __init__(self):
        GeneralBrowser.__init__(self)

        self.get_version_cmd = []
        if self.os.lower() == 'windows':
            self._chrome = App("Chrome")
            self.get_version_cmd = [["reg", "query",
                                     "HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome",
                                     "/v", "DisplayVersion"],
                                    ['reg', 'query', 'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v',
                                     'version']]
        elif self.os.lower() == 'linux':
            self._chrome = App("Chrome")
            self.get_version_cmd = [["google-chrome", "--version"]]
        elif self.os.lower() == 'mac':
            self._chrome = App("Google Chrome")
            self.get_version_cmd = [['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version']]
        self.current_version = self.get_chrome_version()

    def get_chrome_version(self):
        for version_cmd in self.get_version_cmd:
            if subprocess.call(version_cmd) == 0:
                version = subprocess.check_output(version_cmd)
                version_major = int(re.findall(r'\b\d+\b', version)[0])
                return version_major
        return 0

    # Need further permission in Mac OS X and might not be available in windows
    def launchBrowser(self):
        if self._chrome.isRunning():
            self._chrome.close()
        self._chrome.open()

    # Focus on launched Chrome Browser
    def focus(self):
        self._chrome.focus()

    # Wait for URL bar to appear
    def clickBar(self):
        urlbar_pics = ['pics/chrome_urlbar_53.png', 'pics/chrome_urlbar.png']
        for urlbar_pic in urlbar_pics:
            if exists(Pattern(urlbar_pic).similar(0.70)):
                click(Pattern(urlbar_pic).similar(0.70).targetOffset(-40, 0))
                break

    # Launch or close web console for developer
    def triggerConsole(self):
        if self.os.startswith("M"):
            type("j", self.control + Key.ALT)
        else:
            type("j", self.control + Key.SHIFT)

    # Get information from web console, e.g. info = "window.performance.timing"
    def getConsoleInfo(self, info):
        self.triggerConsole()
        wait(Pattern("pics/chrome_webconsole_arrow.png").similar(0.85).targetOffset(14, 1))
        click(Pattern("pics/chrome_webconsole_arrow.png").similar(0.85).targetOffset(14, 1))
        type("copy(" + info + ")")
        type(Key.ENTER)
        self.triggerConsole()
        return Env.getClipboard().strip()

    # Prevent cursor twinkling on screen
    def switchToContentWindow(self):
        type(Key.TAB)


class Firefox(GeneralBrowser):
    def __init__(self):
        GeneralBrowser.__init__(self)
        self._ff = App("Firefox")

    # Need further permission in Mac OS X and might not be available in windows
    # Might not working for Firefox (need alternative launch)
    def launchBrowser(self):
        if self._ff.isRunning():
            self._ff.close()
        self._ff.open()

    # Focus on launched Firefox Browser
    def focus(self):
        self._ff.focus()

    # Wait for URL bar to appear
    def clickBar(self):
        urlbar_pics = ['pics/ff_urlbar_black.png', 'pics/ff_urlbar_gray.png']
        for urlbar_pic in urlbar_pics:
            if exists(Pattern(urlbar_pic).similar(0.70)):
                click(Pattern(urlbar_pic).similar(0.70).targetOffset(-80, 0))
                break

    # Launch web console for developer
    def triggerConsole(self):
        type("k", self.control + Key.SHIFT)

    def closeConsole(self):
        type(Key.F12)

    # Get information from web console, e.g. info = "window.performance.timing"
    def getConsoleInfo(self, info, pre_command=""):
        self.triggerConsole()
        wait(Pattern("pics/ff_webconsole_arrow.png").similar(0.85).targetOffset(14, 1))
        click(Pattern("pics/ff_webconsole_arrow.png").similar(0.85).targetOffset(14, 1))
        if pre_command:
            type(pre_command)
            type(Key.ENTER)
        wait(2)
        type("copy(" + info + ")")
        type(Key.ENTER)
        return Env.getClipboard().strip()

    # Prevent cursor twinkling on screen
    def switchToContentWindow(self):
        type(Key.TAB)
        wait(3)
        type(Key.TAB)

    def profilerTrigger(self):
        type("1", Key.CTRL + Key.SHIFT)

    def profileAnalyze(self):
        type("2", Key.CTRL + Key.SHIFT)
        wait(Pattern("pics/cleopatra_complete.png"), 1 * 60 * 60)
        wait(Pattern("pics/cleopatra_geckomain.png"), 30 * 60)
        wait(30)

    def profilerMark_3(self):
        type("3", Key.CTRL + Key.SHIFT)

    def profilerMark_4(self):
        type("4", Key.CTRL + Key.SHIFT)

    def profilerMark_5(self):
        type("5", Key.CTRL + Key.SHIFT)

    def profilerMark_6(self):
        type("6", Key.CTRL + Key.SHIFT)

    # Ctrl + Shift + 7 and Ctrl + Shift + 8 will disable due to conflict key combination with google doc
    # updated 2016.05.23

    def profilerMark_9(self):
        type("9", Key.CTRL + Key.SHIFT)

    def profilerMark_0(self):
        type("0", Key.CTRL + Key.SHIFT)
