sys.path.append(sys.argv[2])
import browser

ff = browser.Firefox()
wait(2)
ff.focus()
ff.triggerNetwork()
