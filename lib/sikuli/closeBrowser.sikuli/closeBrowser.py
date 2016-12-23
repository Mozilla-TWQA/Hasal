# We will take sys.argv[1] as browser name
browser_name = sys.argv[1]
platform = sys.argv[2]
sys.path.append(sys.argv[3])

CMD_CLOSE = ('w', Key.CTRL)
if platform == 'darwin':
    CMD_CLOSE = ('q', Key.CMD)
elif platform == 'win32':
    CMD_CLOSE = ('q', Key.SHIFT + Key.CTRL)
elif platform == 'linux2':
    CMD_CLOSE = ('q', Key.SHIFT + Key.CTRL)

if browser_name == "chrome":
    browser = App("Google Chrome")
else:
    browser = App(browser_name)
browser.focus()

# Do 10 times before final forced shut down App
for i in range(10):
    if browser.window() or browser.running:
        browser.focus()
        type(*CMD_CLOSE)
        wait(0.5)

# Try to close the app one last time
if browser.window() or browser.running:
    browser.focus()
    browser.close()
