from sikuli import *  # NOQA
import json


class General():
    def __init__(self):
        self.os = str(Env.getOS())
        self.os_version = str(Settings.getOSVersion())

        if self.os.lower() == 'mac':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL

    # This will take in an array of key combinations like [[Key.Enter], [Key.ENTER, Key.CTRL], ["8", Key.CTRL+Key.SHIFT]]
    def key_actions(self, array):
        for action in array:
            sleep(0.3)
            type(*action)

    # Use "highlight" or "popup" to make an anchor for current video
    # style == 0: hightlight, input should be image location
    # style == 1: popup, input should be text
    def img_locator(self, inputc, style=1):
        if style == 1:
            popup(inputc)
        elif style == 0:
            find(inputc).highlight(1)

    def dumpToJson(self, data, filename, mode="w+"):
        with open(filename, mode) as f:
            json.dump(data, f, indent=2)

    def updateJson(self, data, filename, mode="r+"):
        with open(filename, mode) as fh:
            timestamp = json.load(fh)
            timestamp.update(data)
            fh.seek(0)
            fh.write(json.dumps(timestamp))

    def writeToFile(self, data, filename, mode="w+"):
        with open(filename, mode) as f:
            f.write(data)

    def copy(self):
        type("c", self.control)

    def cut(self):
        type("x", self.control)

    def paste(self):
        type("v", self.control)

    def delete(self):
        if self.os.lower() == 'mac':
            type(Key.DELETE)
        else:
            type(Key.BACKSPACE)

    def capLock(self, lock):
        if lock != Key.isLockOn(Key.CAPS_LOCK):
            type(Key.CAPS_LOCK)

    def select_all(self):
        type("a", self.control)

    def page_end(self):
        type(Key.END, self.control)

    def page_start(self):
        type(Key.HOME, self.control)

    def infolog_enable(self, choice=True):
        """
        Enable `Settings.ActionLogs` and `Settings.InfoLogs` when choice is True or 1.
        Disable when choice is False or 0.
        @param choice: True or False
        @return: True for enable, False for disable
        """
        value = 1 if bool(choice) else 0
        Settings.ActionLogs = value
        Settings.InfoLogs = value
        return bool(choice)

    def is_infolog_enabled(self):
        """
        Return True if any one of `Settings.ActionLogs` and `Settings.InfoLogs` is 1 (enabled).
        @return: True or False
        """
        return bool(Settings.ActionLogs) or bool(Settings.InfoLogs)

    def system_print(self, content):
        sys.stdout.write(content + '\n')
        sys.stdout.flush()


class WebApp(object):
    """
    The General Web App library for Sikuli cases.
    The component structure:
        <COMPONENT-NAME> = [
            [<COMPONENT-IMAGE-PLATFORM-FOO>, <OFFSET-X>, <OFFSET-Y>],
            [<COMPONENT-IMAGE-PLATFORM-BAR>, <OFFSET-X>, <OFFSET-Y>]
        ]
    """

    def __init__(self):
        self.common = common.General()
        # Using Env because of sikuli issue from https://bugs.launchpad.net/sikuli/+bug/1514007
        self.os = str(Env.getOS()).lower()

        if self.os == 'mac':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

    def _wait_for_loaded(self, component, similarity=0.70):
        """
        Wait for component loaded, max 5 sec
        @param component: The waiting component
        @param similarity: The similarity of component. Default: 0.70.
        """
        for counter in range(50):
            for pic, _, _ in component:
                if exists(Pattern(pic).similar(similarity), 0.1):
                    break
        wait(Pattern(pic).similar(0.70), 1)

    def _click(self, action_name, component, similarity=0.70):
        """
        Click the component base on the specify image, offset, and similarity.
        @param action_name: The action name, which will be printed to stdout before click.
        @param component: The component you want to click. ex: GMAIL_REPLY.
        @param similarity: The similarity of image. Default: 0.70.
        @return: location
        """
        for counter in range(50):
            for pic, offset_x, offset_y in component:
                p = Pattern(pic).similar(similarity).targetOffset(offset_x, offset_y)
                if exists(p, 0.1):
                    self.common.system_print(action_name)
                    click(p)
                    loc = find(p).getTarget()
                    return loc
        raise Exception('Cannot {action}'.format(action=action_name))

    def _il_click(self, action_name, component, width, height, similarity=0.70):
        """
        This `_il_click` method is written for detecting Input Latency.
        It will break down the `click` to `hover`, `mousedown`, `log`, and `mouseup`

        @param action_name: The action name, which will be printed to stdout after mousedown.
        @param component: The component you want to click. ex: GMAIL_REPLY.
        @param width: the screen capture width.
        @param height: the screen capture height.
        @param similarity: The similarity of image. Default: 0.70.
        @return: location, screenshot for input latency, timestamp between mousedown and mouseup.
        """
        for counter in range(50):
            for pic, offset_x, offset_y in component:
                p = Pattern(pic).similar(similarity).targetOffset(offset_x, offset_y)
                if exists(p, 0.1):
                    # Hover
                    hover(p)
                    # Mouse Down
                    mouseDown(Button.LEFT)

                    # Screenshot and get time for Input Latency
                    screenshot = capture(0, 0, width, height)
                    current_time = time.time()

                    # Print log message for recording
                    self.common.system_print(action_name)

                    # Mouse Up
                    mouseUp(Button.LEFT)
                    # Get location
                    loc = find(p).getTarget()

                    # Return location, screenshot, and time
                    return loc, screenshot, current_time
        raise Exception('Cannot {action}'.format(action=action_name))
