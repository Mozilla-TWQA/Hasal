import os
import urllib2
import xml.etree.ElementTree

# initialize variables
userId=""
userName=""

# get necessary enviroment variables from os
build_url = os.environ['BUILD_URL']
full_url = build_url + "api/xml?xpath=//action/cause"
print full_url

# get the name of whom triggered this build
data = urllib2.urlopen(full_url).read()
xml_data = xml.etree.ElementTree.fromstring(data)

# if user didn't login, the userId will be empty
for node in xml_data:
    if node.tag == "userId":
        userId = node.text
    elif node.tag == "userName":
        userName = node.text

# put it into a file to inject the enviroment
f = open("temp_env", "w")
f.write("Trigger=" + userName + "(" + userId + ")")
