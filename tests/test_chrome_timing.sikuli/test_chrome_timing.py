sys.path.append(sys.argv[2])
import browser
import common


com = common.General()
chrome = browser.Chrome()

wait(2)
chrome.focus()
chrome.getConsoleInfo("window.performance.timing")

wait(1)
com.dumpToJson(Env.getClipboard(), "timing" + sys.argv[1])
