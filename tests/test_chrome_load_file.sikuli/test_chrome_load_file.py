import browser
import common
import sys


com = common.General()
chrome = browser.Chrome()

chrome.clickBar()
chrome.enterLink("https://docs.google.com/document/d/1EpYUniwtLvBbZ4ECgT_vwGUfTHKnqSWi7vgNJQBemFk/edit?usp=sharing")

wait(6)
chrome.getConsoleInfo("window.performance.timing")
com.dumpToJson(Env.getClipboard(), "timing" + sys.argv[1])

