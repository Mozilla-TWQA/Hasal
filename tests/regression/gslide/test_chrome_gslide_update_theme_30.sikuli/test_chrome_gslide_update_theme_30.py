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
wait(gs.mix_content_30_list_original)

type(Key.END)
sleep(1)
wait(gs.mix_content_30_list_final)
gs.invoke_theme_list()
click(gs.blank_theme)
if not waitVanish(gs.mix_content_30_list_final):
    exit(1)
