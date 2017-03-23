# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gslide

com = common.General()
chrome = browser.Chrome()
gs = gslide.gSlide('chrome')

chrome.clickBar()
chrome.enterLink(sys.argv[3])
setAutoWaitTimeout(10)

sleep(2)
gs.wait_for_loaded()
wait(gs.slides_5_list_original)
wait(gs.theme_mozilla_tag_red)

gs.invoke_layout_list()
type(Key.DOWN)
sleep(0.5)
type(Key.DOWN)
sleep(0.5)
type(Key.ENTER)
if not waitVanish(gs.theme_mozilla_tag_red):
    exit(1)
