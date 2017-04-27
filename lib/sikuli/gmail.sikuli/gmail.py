import os
import time

from sikuli import *  # NOQA
import common


class gMail(object):

    GMAIL_COMPOSE = [
        [os.path.join('pics', 'compose_btn_mac.png'), 0, 0],
    ]

    GMAIL_REPLY = [
        [os.path.join('pics', 'reply_btn_mac.png'), 0, 0],
    ]

    GMAIL_SEND = [
        [os.path.join('pics', 'send_btn_mac.png'), 0, 0],
    ]

    GMAIL_FIRST_MAIL = [
        [os.path.join('pics', 'more_btn_mac.png'), 0, 40],
    ]

    def __init__(self):
        self.common = common.General()
        # Using Env because of sikuli issue from https://bugs.launchpad.net/sikuli/+bug/1514007
        self.os = str(Env.getOS()).lower()

        if self.os == 'mac':
            self.control = Key.CMD
        else:
            self.control = Key.CTRL
            self.alt = Key.ALT

    def wait_for_loaded(self):
        # wait for loaded, max 5 sec
        for counter in range(50):
            for pic, _, _ in gMail.GMAIL_COMPOSE:
                if exists(Pattern(pic).similar(0.70), 0.1):
                    break
        wait(Pattern(pic).similar(0.70), 1)

    def _click(self, action_name, component):
        for counter in range(50):
            for pic, offset_x, offset_y in component:
                p = Pattern(pic).similar(0.70).targetOffset(offset_x, offset_y)
                if exists(p, 0.1):
                    self.common.system_print(action_name)
                    click(p)
                    loc = find(p).getTarget()
                    return loc
        raise Exception('Cannot {action}'.format(action=action_name))

    def _il_click(self, action_name, component, width, height):
        """
        This method is written for detecting Input Latency.
        It will break down the `click` to `hover`, `mousedown`, `log`, and `mouseup`

        @param action_name: The action name, which will be printed to stdout after mousedown.
        @param component: Which component you want to click. ex: GMAIL_REPLY.
        @param width: the screen capture width.
        @param height: the screen capture height.
        @return:
        """
        for counter in range(50):
            for pic, offset_x, offset_y in component:
                p = Pattern(pic).similar(0.70).targetOffset(offset_x, offset_y)
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

    def click_first_mail(self):
        return self._click(action_name='Click First Mail', component=gMail.GMAIL_FIRST_MAIL)

    def il_click_first_mail(self, width, height):
        return self._il_click(action_name='Click First Mail',
                              component=gMail.GMAIL_FIRST_MAIL,
                              width=width,
                              height=height)

    def click_reply_btn(self):
        return self._click(action_name='Click Reply Button', component=gMail.GMAIL_REPLY)

    def il_click_reply_btn(self, width, height):
        return self._il_click(action_name='Click Reply Button',
                              component=gMail.GMAIL_REPLY,
                              width=width,
                              height=height)

    def click_compose_btn(self):
        return self._click(action_name='Click Compose Button', component=gMail.GMAIL_COMPOSE)

    def il_click_compose_btn(self, width, height):
        return self._il_click(action_name='Click Compose Button',
                              component=gMail.GMAIL_COMPOSE,
                              width=width,
                              height=height)
