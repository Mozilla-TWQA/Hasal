# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gsheet

com = common.General()
chrome = browser.Chrome()
gs = gsheet.gSheet()

chrome.clickBar()
chrome.enterLink(sys.argv[3])

sleep(2)
gs.wait_for_loaded()

gs.delete_highlight_cell()