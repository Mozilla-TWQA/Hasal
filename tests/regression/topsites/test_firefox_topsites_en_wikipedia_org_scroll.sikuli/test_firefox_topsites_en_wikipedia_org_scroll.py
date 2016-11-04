
sys.path.append(sys.argv[2])
import browser
import common

com = common.General()
ff = browser.Firefox()

ff.clickBar()
ff.enterLink(sys.argv[3])

sleep(2)
wait(Pattern('en_wikipedia_org.png').similar(0.80), 60)

icon_loc = wait(Pattern('en_wikipedia_org.png').similar(0.80), 60).getTarget()
x_offset = 0
y_offset = 150
inside_window = Location(icon_loc.getX() + x_offset, icon_loc.getY() + y_offset)

mouseMove(inside_window)
wheel(WHEEL_DOWN, 100)
wheel(WHEEL_UP, 100)
