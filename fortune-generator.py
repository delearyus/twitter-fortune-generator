#!/usr/bin/env python

import sys
import time
import shutil
from subprocess import call
import os
import argparse

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

#----[ Privelege Check ]------------------------------------------------------#

if os.geteuid() != 0:
    print("This script needs to be run as root.")
    sys.exit(1)

#----[ Arg parsing ]----------------------------------------------------------#

parser = argparse.ArgumentParser()
parser.add_argument("screen_name",
                    help="Twitter handle of user to pull from")

parser.add_argument("-l","--nolinks",
                    help="filter out tweets with links",
                    action="store_true")

parser.add_argument("-m","--nomentions",
                    help="filter out tweets with mentions",
                    action="store_true")

args = parser.parse_args()

#----[ Api initialization ]---------------------------------------------------#

api = twitter.Api(consumer_key=keys.consumer_key,
                  consumer_secret=keys.consumer_secret,
                  access_token_key=keys.access_token,
                  access_token_secret=keys.access_secret)

statuses = set()
screen_name = args.screen_name

temp = ["placeholder"]
oldestid = 1000000000000000000

#----[ Api call loop ]--------------------------------------------------------#

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

#----[ Filtering ]------------------------------------------------------------#

if args.nolinks:
    filteredstatuses = {x for x in statuses if "http" not in x}

    text = "Filtered out {} statuses with embedded links"
    print(text.format(len(statuses) - len(filteredstatuses)))

    statuses = filteredstatuses

if args.nomentions:
    filteredstatuses = {x for x in statuses if "@" not in x}

    text = "Filtered out {} statuses with mentions"
    print(text.format(len(statuses) - len(filteredstatuses)))
    
    statuses = filteredstatuses

#----[ File Output ]----------------------------------------------------------#

datfile = open(screen_name, "w")

for i in statuses:
    datfile.write(i)
    datfile.write("\n%\n")

datfile.close()

#----[ Datfile Generation and Installation ]----------------------------------#

call(["strfile", "-c", "%", datfile.name, datfile.name + ".dat"])

if not os.path.exists("/usr/local/share/fortune"):
    os.makedir("/usr/local/share/fortune")

try:
    os.remove("/usr/local/share/fortune/" + datfile.name)
except FileNotFoundError:
    print("fortune file not found, not deleting it")

try:
    os.remove("/usr/local/share/fortune/" + datfile.name + ".dat")
except FileNotFoundError:
    print("dat file not found, not deleting it")


shutil.move(datfile.name, "/usr/local/share/fortune")
shutil.move(datfile.name + ".dat", "/usr/local/share/fortune")

print("files installed successfully!")
print("use fortune {} to generate fortunes".format(datfile.name))
