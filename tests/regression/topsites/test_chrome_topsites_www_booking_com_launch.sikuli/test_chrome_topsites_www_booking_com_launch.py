
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ch = browser.Chrome()

ch.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('www_booking_com.png').similar(0.80), 60)
