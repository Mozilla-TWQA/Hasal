
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('en_wikipedia_org.png').similar(0.80), 60)
