sys.path.append(sys.argv[2])
import browser
import common


com = common.General()
chrome = browser.Chrome()

wait(2)
chrome.focus()
chrome.switchToContentWindow()
wait(1)
