import os
import time

from sikuli import *  # NOQA
import common


class gMail(object):
    """
    The Gmail library for Sikuli cases.
    The component structure:
        <COMPONENT-NAME> = [
            [<COMPONENT-IMAGE-PLATFORM-FOO>, <OFFSET-X>, <OFFSET-Y>],
            [<COMPONENT-IMAGE-PLATFORM-BAR>, <OFFSET-X>, <OFFSET-Y>]
        ]
    """

    GMAIL_COMPOSE = [
        [os.path.join('pics', 'compose_btn_win.png'), 0, 0],
        [os.path.join('pics', 'compose_btn_mac.png'), 0, 0],
    ]

    GMAIL_REPLY = [
        [os.path.join('pics', 'reply_btn_win.png'), 0, 0],
        [os.path.join('pics', 'reply_btn_mac.png'), 0, 0],
    ]

    GMAIL_SEND = [
        [os.path.join('pics', 'send_btn_win.png'), 0, 0],
        [os.path.join('pics', 'send_btn_mac.png'), 0, 0],
    ]

    GMAIL_FIRST_MAIL_WITH_CATEGORY_BAR = [
        [os.path.join('pics', 'primary_tab_win.png'), 60, 35],
        [os.path.join('pics', 'primary_tab_mac.png'), 60, 45],
    ]

    GMAIL_FIRST_MAIL = [
        [os.path.join('pics', 'more_btn_win.png'), 0, 40],
        [os.path.join('pics', 'more_btn_mac.png'), 0, 40],
    ]

    GMAIL_REPLY_DEL = [
        [os.path.join('pics', 'reply_del_btn_win.png'), -30, -5],
        [os.path.join('pics', 'reply_del_btn_mac.png'), -28, 0],
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

    def wait_for_loaded(self, similarity=0.70):
        """
        Wait for Gmail loaded, max 5 sec
        @param similarity: The similarity of GMAIL_COMPOSE component. Default: 0.70.
        """
        for counter in range(50):
            for pic, _, _ in gMail.GMAIL_COMPOSE:
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

    def click_first_mail(self):
        """
        Click the first mail on NO CATEGORY BAR page.
        """
        return self._click(action_name='Click First Mail',
                           component=gMail.GMAIL_FIRST_MAIL)

    def il_click_first_mail(self, width, height):
        """
        Click the first mail on NO CATEGORY BAR page.
        (Input Latency)
        """
        return self._il_click(action_name='Click First Mail',
                              component=gMail.GMAIL_FIRST_MAIL,
                              width=width,
                              height=height)

    def click_first_mail_with_category_bar(self):
        """
        Click the first mail on CATEGORY BAR page (Default Input View).
        """
        return self._click(action_name='Click First Mail',
                           component=gMail.GMAIL_FIRST_MAIL_WITH_CATEGORY_BAR,
                           similarity=0.85)

    def il_click_first_mail_with_category_bar(self, width, height):
        """
        Click the first mail on CATEGORY BAR page (Default Input View).
        (Input Latency)
        """
        return self._il_click(action_name='Click First Mail',
                              component=gMail.GMAIL_FIRST_MAIL_WITH_CATEGORY_BAR,
                              width=width,
                              height=height,
                              similarity=0.85)

    def click_reply_btn(self):
        """
        Click reply button on the top-right side.
        """
        return self._click(action_name='Click Reply Button',
                           component=gMail.GMAIL_REPLY)

    def il_click_reply_btn(self, width, height):
        """
        Click reply button on the top-right side.
        (Input Latency)
        """
        return self._il_click(action_name='Click Reply Button',
                              component=gMail.GMAIL_REPLY,
                              width=width,
                              height=height)

    def click_reply_del_btn(self):
        """
        Click delete button on the bottom-left side in reply window.
        """
        return self._click(action_name='Click Reply Delete Button',
                           component=gMail.GMAIL_REPLY_DEL,
                           similarity=0.85)

    def il_click_reply_del_btn(self, width, height):
        """
        Click delete button on the bottom-left side in reply window.
        (Input Latency)
        """
        return self._il_click(action_name='Click Reply Delete Button',
                              component=gMail.GMAIL_REPLY_DEL,
                              width=width,
                              height=height,
                              similarity=0.85)

    def click_compose_btn(self):
        """
        Click compose button on the top-left side.
        """
        return self._click(action_name='Click Compose Button',
                           component=gMail.GMAIL_REPLY_DEL)

    def il_click_compose_btn(self, width, height):
        """
        Click compose button on the top-left side.
        (Input Latency)
        """
        return self._il_click(action_name='Click Compose Button',
                              component=gMail.GMAIL_COMPOSE,
                              width=width,
                              height=height)
