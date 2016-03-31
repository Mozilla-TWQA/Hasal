# Wait for URL bar to appear
wait(Pattern("chrome_urlbar.png").similar(0.85).targetOffset(-40,0))
click(Pattern("chrome_urlbar.png").similar(0.85).targetOffset(-40,0))

# Enter the link and open google document
type("http://goo.gl/3GR0GN")
type(Key.ENTER)