# We will take sys.argv[1] as browser name
browser_name = sys.argv[1]
sys.path.append(sys.argv[2])

browser = App(browser_name)
browser.focus()

# Do 10 times before final forced shut down App
for i in range(10):
    if browser.window():
        wait(1)
        if "firefox" in browser_name:
            type("w", Key.CTRL)
        elif "chrome" in browser_name:
            type("w", Key.SHIFT+Key.CTRL)

# Try to close the app one last time
if browser.window():
    wait(1)
    browser.close()
