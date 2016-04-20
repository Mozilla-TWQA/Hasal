# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import browser
import common
import gdoc

com = common.General()
chrome = browser.Chrome()
gd = gdoc.gDoc()

chrome.clickBar()
chrome.enterLink(sys.argv[3])
sleep(5)
gd.wait_for_loaded()

# Call the "Find and replace" window
type("h", Key.CTRL)

# Type the keyword that you want to search
type("Mozilla")

# Type the keyword that you want to replace to be 
type(Key.TAB)
type("Firefox")

# Click "Replace All" button
type(Key.TAB)
type(Key.TAB)
type(Key.TAB)
type(Key.ENTER)

gdoc.deFoucsContentWindow()

