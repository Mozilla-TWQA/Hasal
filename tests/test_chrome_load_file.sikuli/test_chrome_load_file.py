# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
library_path = "/".join(getParentFolder().split("/")[:-2]) + "/lib/sikuli"
sys.path.append(library_path)
import browser

chrome = browser.Chrome()
chrome.clickBar()
chrome.enterLink("https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit?usp=sharing")

wait(5)
chrome.getConsoleInfo("window.performance.timing")
