import os
import sys
import time
import getopt
import random
import string
from selenium import webdriver

website = "http://www.facebook.com"
profile_page = "https://www.facebook.com/profile.php"


def main(argv):
    # get information from argv
    username = ''
    password = ''
    action = ''
    quantity = ''
    text = "All warfare is based on deception. Hence, when we are able to attack, we must seem unable; when using our forces, we must appear inactive; when we are near, we must make the enemy believe we are far away; when far away, we must make him believe we are near. "

    try:
        opts, args = getopt.getopt(argv, "hu:p:a:q:", ["user=", "passwd=", "action=", "quantity="])
    except getopt.GetoptError:
        print 'Enter your username and password for facebook if you want.'
        print 'test.py -u <username> -p <password> -a (create/delete) -q (number)'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -u <username> -p <password> -a (create/delete) -q (number)'
            sys.exit()
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-p", "--passwd"):
            password = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-q", "--quantity"):
            quantity = arg

    # creating path
    current_platform_name = sys.platform
    DEFAULT_HASAL_DIR = "/".join(os.getcwd().split("/")[:-2])
    DEFAULT_THIRDPARTY_DIR = os.path.join(DEFAULT_HASAL_DIR, "thirdParty")
    DEFAULT_GECKODRIVER_DIR = os.path.join(DEFAULT_THIRDPARTY_DIR, "geckodriver")

    # adding geckodriver path
    if DEFAULT_GECKODRIVER_DIR not in os.environ['PATH']:
        if current_platform_name == "darwin" or current_platform_name == "linux2":
            os.environ['PATH'] += ":" + DEFAULT_GECKODRIVER_DIR
        else:
            os.environ['PATH'] += ";" + DEFAULT_GECKODRIVER_DIR + ";"

    # getting website opened
    driver = webdriver.Firefox()
    driver.get(website)

    # try to login if there are creditials in parameters
    time.sleep(2)
    account_input = driver.find_element_by_id("email")
    password_input = driver.find_element_by_id("pass")
    login_button = driver.find_element_by_id("loginbutton")

    account_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    # try to create or delete content
    time.sleep(2)
    driver.get(profile_page)
    if action == "create":
        if quantity == '':
            run_time = 1
        else:
            run_time = int(quantity)

        for i in range(run_time):
            random_text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            message_box = driver.find_element_by_name("xhpc_message_text")
            message_box.send_keys(text + random_text)
            time.sleep(2)
            buttons = driver.find_elements_by_tag_name("button")
            for button in buttons:
                if button.get_attribute("data-testid") == "react-composer-post-button":
                    button.click()
            time.sleep(5)

    elif action == "delete":
        if quantity == '':
            run_time = 1
        else:
            run_time = int(quantity)

        for i in range(run_time):
            driver.find_elements_by_css_selector("div.fbUserContent a")[0].click()
            time.sleep(2)

            delete_buttons = driver.find_elements_by_css_selector("li a[data-feed-option-name=FeedDeleteOption]")
            for delete_button in delete_buttons:
                if delete_button.is_displayed():
                    delete_button.click()
            time.sleep(2)

            delete_buttons = driver.find_elements_by_xpath("//button[text()='Delete Post']")
            for delete_button in delete_buttons:
                if delete_button.is_displayed():
                    delete_button.click()
            time.sleep(5)

if __name__ == "__main__":
    main(sys.argv[1:])
