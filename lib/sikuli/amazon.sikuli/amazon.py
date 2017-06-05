import os

from sikuli import *  # NOQA
from common import WebApp


class Amazon(WebApp):
    """
    The Amazon library for Sikuli cases.
    The component structure:
        <COMPONENT-NAME> = [
            [<COMPONENT-IMAGE-PLATFORM-FOO>, <OFFSET-X>, <OFFSET-Y>],
            [<COMPONENT-IMAGE-PLATFORM-BAR>, <OFFSET-X>, <OFFSET-Y>]
        ]
    """

    AMAZON_LOGO = [
        [os.path.join('pics', 'amazon_logo.png'), 0, 0],
    ]

    AMAZON_SEARCH_BTN = [
        [os.path.join('pics', 'search_button.png'), 0, 0],
    ]

    AMAZON_SEARCH_FIELD = [
        [os.path.join('pics', 'search_button.png'), -80, 0],
    ]

    AMAZON_PRODUCT_THUMBNAIL = [
        [os.path.join('pics', 'customers_text.png'), 665, 140],
    ]

    AMAZON_CUSTOMER_TEXT = [
        [os.path.join('pics', 'customers_text.png'), 0, 0],
    ]

    AMAZON_FUNCTION_UNDER_SEARCH_FIELD = [
        [os.path.join('pics', 'function_under_search_field_guest_win7.png'), 0, 0],
        [os.path.join('pics', 'function_under_search_field_guest_win10.png'), 0, 0],
        [os.path.join('pics', 'function_under_search_field_moztpeqa_win7.png'), 0, 0],
        [os.path.join('pics', 'function_under_search_field_moztpeqa_win10.png'), 0, 0],
    ]

    def wait_for_logo_loaded(self, similarity=0.70):
        """
        @param similarity: The similarity of AMAZON_LOGO component. Default: 0.70.
        """
        return self._wait_for_loaded(component=Amazon.AMAZON_LOGO, similarity=similarity)

    def wait_for_search_button_loaded(self, similarity=0.70):
        """
        @param similarity: The similarity of AMAZON_SEARCH_BTN component. Default: 0.70.
        """
        return self._wait_for_loaded(component=Amazon.AMAZON_SEARCH_BTN, similarity=similarity)

    def wait_for_func_field_loaded(self, similarity=0.70):
        """
        @param similarity: The similarity of AMAZON_FUNCTION_UNDER_SEARCH_FIELD component. Default: 0.70.
        """
        return self._wait_for_loaded(component=Amazon.AMAZON_FUNCTION_UNDER_SEARCH_FIELD, similarity=similarity)

    def wait_for_customer_text_loaded(self, similarity=0.70):
        """
        @param similarity: The similarity of AMAZON_CUSTOMER_TEXT component. Default: 0.70.
        """
        return self._wait_for_loaded(component=Amazon.AMAZON_CUSTOMER_TEXT, similarity=similarity)

    def click_search_field(self):
        """
        Click search field near the search button.
        """
        return self._click(action_name='Click Search Field',
                           component=Amazon.AMAZON_SEARCH_FIELD,
                           wait_component=Amazon.AMAZON_SEARCH_BTN)

    def il_hover_fifth_customer_watched_product(self, width, height):
        """
        Hover the fifth product thumbnail from customer also watched list
        """
        return self.il_hover(action_name='Hover Product Thumbnail',
                             component=Amazon.AMAZON_PRODUCT_THUMBNAIL,
                             width=width,
                             height=height,
                             wait_component=Amazon.AMAZON_CUSTOMER_TEXT)

    def il_type_key_down_search_suggestion(self, width, height):
        """
        Type key down on search suggestions
        """
        return self.il_key_type(key=Key.DOWN,
                                action_name='Type Key Down',
                                width=width,
                                height=height)
