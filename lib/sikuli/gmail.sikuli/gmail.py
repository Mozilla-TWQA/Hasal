import os

from sikuli import *  # NOQA
from common import WebApp


class gMail(WebApp):
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

    GMAIL_SETTINGS = [
        [os.path.join('pics', 'settings_btn_win.png'), 0, 0],
    ]

    GMAIL_REPLY = [
        [os.path.join('pics', 'reply_btn_win.png'), 0, 0],
        [os.path.join('pics', 'reply_btn_mac.png'), 0, 0],
    ]

    GMAIL_SEND = [
        [os.path.join('pics', 'send_btn_win.png'), 0, 0],
        [os.path.join('pics', 'send_btn_mac.png'), 0, 0],
    ]

    GMAIL_TYPE_FOR_REPLY = [
        [os.path.join('pics', 'type_for_reply_btn_win.png'), 0, 0],
        [os.path.join('pics', 'type_for_reply_btn_chrome_win10.png'), 0, 0],
    ]

    GMAIL_FIRST_MAIL_WITH_CATEGORY_BAR = [
        [os.path.join('pics', 'primary_tab_win.png'), 60, 35],
        [os.path.join('pics', 'primary_tab_mac.png'), 60, 45],
    ]

    GMAIL_FIRST_MAIL = [
        [os.path.join('pics', 'settings_btn_win.png'), 0, 40],
        [os.path.join('pics', 'more_btn_win.png'), 0, 40],
        [os.path.join('pics', 'more_btn_mac.png'), 0, 40],
    ]

    GMAIL_REPLY_DEL = [
        [os.path.join('pics', 'reply_del_btn_win.png'), -30, -5],
        [os.path.join('pics', 'reply_del_btn_chrome_win10.png'), -20, 0],
        [os.path.join('pics', 'reply_del_btn_mac.png'), -28, 0],
    ]

    def wait_for_loaded(self, similarity=0.70):
        """
        Wait for Gmail loaded, max 5 sec
        @param similarity: The similarity of GMAIL_COMPOSE and GMAIL_SETTINGS components. Default: 0.70.
        """
        self._wait_for_loaded(component=(gMail.GMAIL_COMPOSE + gMail.GMAIL_SETTINGS),
                              similarity=similarity)

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
