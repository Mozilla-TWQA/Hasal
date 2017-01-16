#This is for jenkins to get trigger information
#"Update build name" plugin is required after executing this python script
import os
import urllib2
import xml.etree.ElementTree

# initialize variables
userId=""
userName=""

# get necessary enviroment variables from os
build_url = os.environ['BUILD_URL']
build_num = os.environ['BUILD_NUMBER']
email = os.environ['Email']
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

# put it into a file to "Update build name" from a file
f = open("temp_env_build_name", "w")
f.write("#" + build_num + " - From: " + userName + "(" + userId + ") Buildof: " + email + " ")
