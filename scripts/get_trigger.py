# This is for Jenkins CI
# Purpose: Get the trigger and create a file for environment injection
import os
import urllib2
import xml.etree.ElementTree

# get necessary enviroment variables from os
job_name = os.environ['JOB_NAME']
build_num = os.environ['BUILD_NUMBER']

# get the name of whom triggered this build
data = urllib2.urlopen("http://10.247.120.208:8080/job/" + job_name + "/" + build_num + "/api/xml?xpath=//action/cause/userId").read()
user = xml.etree.ElementTree.fromstring(data).text

# put it into a file to inject the enviroment
f = open("temp_env", "w")
f.write("Trigger=" + user)
