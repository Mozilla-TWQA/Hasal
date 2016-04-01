# Wait for URL bar to appear
wait(Pattern("ff_urlbar.png").similar(0.70))
click(Pattern("ff_urlbar.png").similar(0.70).targetOffset(-100,0))

# Enter the link and open google document
type("http://goo.gl/3GR0GN")
type(Key.ENTER)