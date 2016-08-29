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

    def post_content(self, location=None, content_type=None, input_string=None):
        if not location or not file_path or not content_type:
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
                self.action_post_text(input_string)
            elif content_type == 'photo_video':
                self.click_post_area_home(type='photo_video')
                self.action_post_upload(input_string)
            elif content_type == 'url':
                self.click_post_area_home(type='center')
                self.action_post_url(location,input_string)
        elif location == 'club':
            if content_type == 'text':
                self.click_post_area_club(type='center')
                self.action_post_text(input_string)
            elif content_type == 'photo_video':
                self.click_post_area_club(type='photo_video')
                self.action_post_upload(input_string)
            elif content_type == 'url':
                self.click_post_area_club(type='center')
                self.action_post_url(location,input_string)
        elif location == 'personal':
            if content_type == 'text':
                self.click_post_area_personal()
                self.action_post_text(input_string)
            elif content_type == 'photo_video':
                print "=== Currently doesn't support post photo/video to personal page. ==="
                return -1
            elif content_type == 'url':
                self.click_post_area_personal()
                self.action_post_url(location,input_string)
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
    def action_post_text(self, string):
        paste(ucode(string))
        sleep(1)
        self.click_post_button()

    # paste file path to file browser, wait for upload finished then post
    def action_post_upload(self, file_path):
        type("a", Key.CTRL)
        type(Key.DELETE)
        paste(file_path)
        type(Key.ENTER)
        while(exists(Pattern("pics/facebook_post_button.png").similar(0.85)) and exists(Pattern("pics/facebook_post_area_focused.png").similar(0.85))):
            self.click_post_button()
            sleep(1)

    # paste url, wait thumbnail shown then post
    def action_post_url(self, location, url):
        paste(url)
        self.wait_post_area_vanish(location)
        sleep(1)
        self.click_post_button()

    # invoke menu of top post from club then delete post
    def action_club_del_post_top(self):
        click(Pattern("pics/facebook_club_post_marker.png").similar(0.85), 10)
        wait(Pattern("pics/facebook_club_delete_post_menu.png"))
        click(Pattern("pics/facebook_club_delete_post_menu.png").targetOffset(0,-10))
        wait(Pattern("pics/facebook_club_delete_post_button.png").similar(0.85), 10)
        click(Pattern("pics/facebook_club_delete_post_button.png").similar(0.85))

    # # invoke menu of top post from home or personal page then delete post
    def action_non_club_del_post_top(self):
        click(Pattern("pics/facebook_non_club_post_marker.png").similar(0.85))
        wait(Pattern("pics/facebook_non_club_delete_post_menu.png"))
        click(Pattern("pics/facebook_non_club_delete_post_menu.png").targetOffset(0,-10))
        wait(Pattern("pics/facebook_non_club_delete_post_button.png").similar(0.85), 10)
        click(Pattern("pics/facebook_non_club_delete_post_button.png").similar(0.85))

    def wait_post_area(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'home':
            wait(Pattern("pics/facebook_home_post_area.png").similar(0.85))
        elif location == 'club':
            wait(Pattern("pics/facebook_club_post_area.png").similar(0.85))
        elif location == 'personal':
            wait(Pattern("pics/facebook_personal_post_area.png").similar(0.85))

    def wait_post_area_vanish(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'home':
            waitVanish(Pattern("pics/facebook_home_post_area.png").similar(0.85))
        elif location == 'club':
            waitVanish(Pattern("pics/facebook_club_post_area.png").similar(0.85))
        elif location == 'personal':
            waitVanish(Pattern("pics/facebook_personal_post_area.png").similar(0.85))

    def wait_del_button_vanish(self, location=None):
        if not location:
            print "[ERROR]: Please specify the location"
            raise Exception

        if location == 'club':
            waitVanish(Pattern("pics/facebook_club_delete_post_button.png").similar(0.85))
        else:
            waitVanish(Pattern("pics/facebook_non_club_delete_post_button.png").similar(0.85))

    def click_post_button(self):
        click(Pattern("pics/facebook_post_button.png").similar(0.85))

    # base on post type to click different areas from home
    def click_post_area_home(self, type='center'):
        if type == 'center':
            click(Pattern("pics/facebook_home_post_area.png").similar(0.85))
            wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))
        elif type == 'photo_video':
            click(Pattern("pics/facebook_home_post_area.png").similar(0.85).targetOffset(-180,-60))
            waitVanish(Pattern("pics/facebook_home_post_area.png").similar(0.85), 10)

    # base on post type to click different areas from club
    def click_post_area_club(self, type='center'):
        if type == 'center':
            click(Pattern("pics/facebook_club_post_area.png").similar(0.85).targetOffset(0,15))
            wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))
        elif type == 'photo_video':
            click(Pattern("pics/facebook_club_post_area.png").similar(0.85).targetOffset(-60, -35))
            wait(Pattern("pics/facebook_club_post_area_upload.png").similar(0.65))
            click(Pattern("pics/facebook_club_post_area_upload.png").similar(0.65).targetOffset(-125, 15)) 
            waitVanish(Pattern("pics/facebook_club_post_area_upload.png").similar(0.65), 10)

    def click_post_area_personal(self):
        click(Pattern("pics/facebook_personal_post_area.png").similar(0.85))
        wait(Pattern("pics/facebook_post_area_focused.png").similar(0.85))

    # return all content from file
    def get_text_from_file(self, file_path):
        f = open(file_path, 'r')
        content = ucode(f.read())
        f.close()
        return content
