#!/usr/bin/env python

import sys
import time
import shutil
from subprocess import call
import os

try:
    import keys
except ImportError:
    print("Keys not found. do you have the proper key file?")
    sys.exit(1)

try:
    import twitter
except ImportError:
    print("python-twitter not found, install with pip install python-twitter")
    sys.exit(1)

#-----------------------------------------------------------------------------#

if os.geteuid() != 0:
    print("This script needs to be run as root.")
    sys.exit(1)

#-----------------------------------------------------------------------------#

api = twitter.Api(consumer_key=keys.consumer_key,
                  consumer_secret=keys.consumer_secret,
                  access_token_key=keys.access_token,
                  access_token_secret=keys.access_secret)

statuses = set()
screen_name = 'dril'

temp = ["placeholder"]
oldestid = 1000000000000000000

#-----------------------------------------------------------------------------#

while (len(temp) > 0):

    try:
        temp = api.GetUserTimeline(screen_name=screen_name,
                                   trim_user=True,
                                   max_id=oldestid)
    except TwitterError:
        print("Request failed, retrying in 5s.")
        time.sleep(5)
        continue

    print("Got {} tweets after id {}".format(len(temp), oldestid))
    oldestid = min([s.id for s in temp], default=2) - 1

    for i in temp:
        statuses.add(i.text)

print("finished!")

print("Found a total of {} unique statuses".format(len(statuses)))

#-----------------------------------------------------------------------------#

filteredstatuses = {x for x in statuses if "http" not in x}

text = "Filtered out {} statuses with embedded links"
print(text.format(len(statuses) - len(filteredstatuses)))

statuses = filteredstatuses

filteredstatuses = {x for x in statuses if "@" not in x}

text = "Filtered out {} statuses with mentions"
print(text.format(len(statuses) - len(filteredstatuses)))

#-----------------------------------------------------------------------------#

datfile = open(screen_name, "w")

for i in filteredstatuses:
    datfile.write(i)
    datfile.write("\n%\n")

datfile.close()

#-----------------------------------------------------------------------------#

call(["strfile", "-c", "%", datfile.name, datfile.name + ".dat"])

try:
    os.remove("/usr/share/fortune/" + datfile.name)
except FileNotFoundError:
    print("fortune file not found, not deleting it")

try:
    os.remove("/usr/share/fortune/" + datfile.name + ".dat")
except FileNotFoundError:
    print("dat file not found, not deleting it")


shutil.move(datfile.name, "/usr/share/fortune")
shutil.move(datfile.name + ".dat", "/usr/share/fortune")

print("files installed successfully!")
print("use fortune {} to generate fortunes".format(datfile.name))
