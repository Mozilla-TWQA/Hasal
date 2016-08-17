sys.path.append(sys.argv[2])
import browser
import common
import gdoc


com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

gd.wait_for_loaded()

wait(Pattern("EditDropdown.png").similar(0.50))
wait(5)

keyword = "OLD"
gd.page_text_generate(keyword, 1)

sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(5)
type(Key.ENTER, Key.CTRL)

gd.page_text_generate(keyword, 1)

sleep(5)
gd.wait_for_loaded()
gd.insert_image_url("https://drive.google.com/file/d/0B9Zi9TqbRWsdM0owSVlmbkRpUFE/view?usp=sharing")
sleep(5)
type(Key.ENTER)
type(Key.ENTER)
sleep(5)
type(Key.ENTER, Key.CTRL)


type("h", Key.CTRL)
wait(Pattern("FindAndReplace.png").similar(0.50))
click(Pattern("FindReplaceInput.png").targetOffset(98,-21))
type(keyword)
click(Pattern("FindReplaceInput.png").targetOffset(98,26))
type("NEW")

for i in range(15):
    wait(Pattern("Replace.png").similar(0.58))
    click(Pattern("Replace.png").similar(0.58))

sleep(2)
gd.deFoucsContentWindow()
