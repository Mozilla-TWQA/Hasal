sys.path.append(sys.argv[2])
import browser

chrome = browser.Chrome()

wait(2)
chrome.focus()
chrome.triggerNetwork()
