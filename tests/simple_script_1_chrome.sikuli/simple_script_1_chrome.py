# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
library_path = "/".join(getParentFolder().split("/")[:-2]) + "/lib/sikuli"
sys.path.append(library_path)
import browser

chrome = browser.Chrome()
chrome.clickBar()
chrome.enterLink("http://goo.gl/3GR0GN")
