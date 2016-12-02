
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ch = browser.Chrome()

ch.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('en_wikipedia_org.png').similar(0.80), 60)
