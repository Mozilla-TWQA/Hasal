from sikuli import *  # NOQA
import os
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

        self.fb_logo = Pattern("pics/facebook_logo.png").similar(0.70)
        self.blue_bar = Pattern("pics/facebook_blue_bar.png").similar(0.70)
        self.search_bar = Pattern("pics/facebook_search_bar.png").similar(0.70)
        self.search_icon = Pattern("pics/facebook_search_icon.png").similar(0.70)
        self.folding_icon = Pattern("pics/facebook_folding_icon.png").similar(0.70)
        self.notification_icon = Pattern("pics/facebook_notification_icon.png").similar(0.70)
        self.post_button = Pattern("pics/facebook_post_button.png").similar(0.70)
        self.post_action = Pattern("pics/facebook_post_action.png").similar(0.70)
        self.home_post_area = Pattern("pics/facebook_home_post_area.png").similar(0.70)
        self.club_post_area = Pattern("pics/facebook_club_post_area.png").similar(0.70)
        self.personal_post_area = Pattern("pics/facebook_personal_post_area.png").similar(0.70)
        self.post_area_focused = Pattern("pics/facebook_post_area_focused.png").similar(0.70)
        self.home_post_area_focused = Pattern("pics/facebook_home_post_area_focused.png").similar(0.70)
        self.club_delete_post_button = Pattern("pics/facebook_club_delete_post_button.png").similar(0.85)
        self.club_post_area_upload = Pattern("pics/facebook_club_post_area_upload.png").similar(0.70)
        self.club_post_marker = Pattern("pics/facebook_club_post_marker.png").similar(0.70)
        self.club_delete_post_menu = Pattern("pics/facebook_club_delete_post_menu.png").similar(0.70)
        self.non_club_delete_post_button = Pattern("pics/facebook_non_club_delete_post_button.png").similar(0.70)
        self.non_club_post_marker = Pattern("pics/facebook_non_club_post_marker.png").similar(0.70)
        self.non_club_post_menu_edit = Pattern("pics/facebook_non_club_post_menu_edit.png").similar(0.70)
        self.non_club_delete_post_menu = Pattern("pics/facebook_non_club_delete_post_menu.png").similar(0.70)
        self.club_post_header = Pattern("pics/facebook_club_post_header.png").similar(0.70)
        self.video_stop_icon = Pattern("pics/facebook_video_stop_icon.png").similar(0.70)
        self.feed_end_reminder = Pattern("pics/facebook_feed_end_reminder.png").similar(0.70)
        self.activity_end_reminder = Pattern("pics/facebook_activity_end_reminder.png").similar(0.70)
        self.share_button = Pattern("pics/facebook_share_button.png").similar(0.70)
        self.share_menu = Pattern("pics/facebook_share_menu.png").similar(0.70)
        self.save_button = Pattern("pics/facebook_save_button.png").similar(0.70)
        self.club_post_menu_delete = Pattern("pics/facebook_club_post_menu_delete.png").similar(0.70)
        self.messenger_header = Pattern("pics/facebook_messenger_header.png").similar(0.70)
        self.right_panel_contact = Pattern("pics/facebook_contact.png").similar(0.70)
        self.chat_tab_close_button = Pattern("pics/facebook_chat_tab_close_button.png").similar(0.70)

        self.sampleImg1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "content", "sample_1.jpg")

    def wait_for_loaded(self):
        wait(self.fb_logo, 15)

    def wait_for_messenger_loaded(self):
        wait(self.messenger_header, 15)

    def focus_window(self):
        click(self.fb_logo.targetOffset(0, 15), 10)

    def post_content(self, location=None, content_type=None, input_string=None):
        if not location or not input_string or not content_type:
            print "[ERROR]: Please specify the location, input_string, and content_type"
            print "Location: home, club, or personal"
            print "Content Type: photo_video, text, or url"
            print "[photo_video] needs file path"
            print "[text] needs string"
            print "[url] needs full url path"
            raise Exception

        if location == 'home':
            if content_type == 'text':
                self.click_post_area_home(type='center')
                self.action_post_text(location, input_string)
            elif content_type == 'photo_video':
                self.click_post_area_home(type='photo_video')
                self.action_post_upload(input_string)
            elif content_type == 'url':
                self.click_post_area_home(type='center')
                self.action_post_url(location, input_string)
        elif location == 'club':
            if content_type == 'text':
                self.click_post_area_club(type='center')
                self.action_post_text(location, input_string)
            elif content_type == 'photo_video':
                self.click_post_area_club(type='photo_video')
                self.action_post_upload(input_string)
            elif content_type == 'url':
                self.click_post_area_club(type='center')
                self.action_post_url(location, input_string)
        elif location == 'personal':
            if content_type == 'text':
                self.click_post_area_personal()
                self.action_post_text(location, input_string)
            elif content_type == 'photo_video':
                print "=== Currently doesn't support post photo/video to personal page. ==="
                return -1
            elif content_type == 'url':
                self.click_post_area_personal()
                self.action_post_url(location, input_string)
        self.wait_post_area(location)
        print('[Facebook] post_content() done.')

    def del_post_top(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'club':
            self.action_club_del_post_top()
        else:
            self.action_non_club_del_post_top()
        self.wait_del_button_vanish(location)
        print('[Facebook] del_post_top() done.')

    # paste string then post
    def action_post_text(self, location, string):
        paste(ucode(string))
        self.wait_post_area_vanish(location)
        sleep(2)
        click(self.post_button)

    # paste file path to file browser, wait for upload finished then post
    def action_post_upload(self, file_path):
        type("a", Key.CTRL)
        type(Key.DELETE)
        paste(file_path)
        type(Key.ENTER)
        while exists(self.post_button) and exists(self.post_area_focused):
            click(self.post_button)
            sleep(1)

    # paste url, wait thumbnail shown then post
    def action_post_url(self, location, url):
        paste(url)
        self.wait_post_area_vanish(location)
        sleep(2)
        click(self.post_button)

    # invoke menu of top post from club then delete post
    def action_club_del_post_top(self):
        click(self.club_post_marker, 10)
        wait(self.club_delete_post_menu)
        click(self.club_delete_post_menu.targetOffset(0, -10))
        wait(self.club_delete_post_button, 10)
        click(self.club_delete_post_button)

    # invoke menu of top post from home or personal page then delete post
    def action_non_club_del_post_top(self):
        click(self.non_club_post_marker)
        wait(self.non_club_delete_post_menu)
        click(self.non_club_delete_post_menu.targetOffset(0, -10))
        wait(self.non_club_delete_post_button, 10)
        click(self.non_club_delete_post_button)

    def wait_post_area(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'home':
            wait(self.home_post_area)
        elif location == 'club':
            wait(self.club_post_area)
        elif location == 'personal':
            wait(self.personal_post_area)

    def wait_post_area_vanish(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'home':
            waitVanish(self.home_post_area)
        elif location == 'club':
            waitVanish(self.club_post_area)
        elif location == 'personal':
            waitVanish(self.personal_post_area)

    def wait_del_button_vanish(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'club':
            waitVanish(self.club_delete_post_button)
        else:
            waitVanish(self.non_club_delete_post_button)

    # base on post type to click different areas from home
    def click_post_area_home(self, type='center'):
        if type == 'center':
            click(self.home_post_area)
            wait(self.home_post_area_focused)
        elif type == 'photo_video':
            click(self.home_post_area.targetOffset(-180, 50))
            waitVanish(self.home_post_area, 10)

    # base on post type to click different areas from club
    def click_post_area_club(self, type='center'):
        if type == 'center':
            click(self.club_post_area.targetOffset(0, 15))
            wait(self.post_area_focused)
        elif type == 'photo_video':
            click(self.club_post_area.targetOffset(-60, -35))
            wait(self.club_post_area_upload)
            click(self.club_post_area_upload.targetOffset(-125, 15))
            waitVanish(self.club_post_area_upload, 10)

    def click_post_area_personal(self):
        click(self.personal_post_area)
        wait(self.post_area_focused)

    # extend a post which is folded
    def extend_post(self):
        click(self.folding_icon)
        waitVanish(self.folding_icon)

    # invoke message list from notification bar
    def invoke_messages(self):
        click(self.notification_icon)
        waitVanish(self.notification_icon)

    def search_content(self, keyword):
        click(self.search_bar)
        paste(keyword)
        wait(self.search_icon)

    # share an enlarged post, which has previewed pop up screen to post
    def share_enlarged_post(self):
        wait(self.post_action)
        click(self.post_action.targetOffset(80, 0))
        waitVanish(self.post_action)
        click(self.post_button)
        waitVanish(self.post_button)

    # share post, e.g., url link or video
    def share_post(self):
        click(self.share_button)
        click(self.share_menu.targetOffset(0, -12))
        waitVanish(self.share_button)
        click(self.post_button)
        waitVanish(self.post_button)

    # return all content from file
    def get_text_from_file(self, file_path):
        f = open(file_path, 'r')
        content = ucode(f.read())
        f.close()
        return content

    # focus on comment box of any post
    def focus_comment_box(self):
        wait(self.post_action)
        click(self.post_action)
