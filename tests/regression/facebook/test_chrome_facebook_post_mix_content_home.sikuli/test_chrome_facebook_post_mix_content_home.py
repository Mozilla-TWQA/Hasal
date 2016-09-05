# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import facebook

com = common.General()
chrome = browser.Firefox()
fb = facebook.facebook()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

sleep(2)
setAutoWaitTimeout(10)
fb.wait_for_loaded()
fb.post_content(location='home', content_type='text',
                input_string='https://www.mozilla.org/en-US/  Answer: Depending on how one distinguishes a different '
                             'Bible version from a revision of an existing Bible version, there are as many as 50 '
                             'different English versions of the Bible. The question then arises: Is there really a '
                             'need for so many different English versions of the Bible? The answer is, of course, no, '
                             'there is no need for 50 different English versions of the Bible. This is especially true '
                             'considering that there are hundreds of languages into which the entire Bible has not yet '
                             'been translated. At the same time, there is nothing wrong with there being multiple '
                             'versions of the Bible in a language. In fact, multiple versions of the Bible can '
                             'actually be an aid in understanding the message of the Bible.')
