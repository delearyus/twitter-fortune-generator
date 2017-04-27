#!/usr/bin/env python

import sys
import time
import shutil
from subprocess import call
import os
import argparse
from requests import ConnectionError
import html

try:
    import keys
except ImportError:
    print("Keys not found. do you have the proper key file?")
    print("If not, register this app with twitter and run `keygen.py`")
    sys.exit(1)

try:
    import twitter
except ImportError:
    print("python-twitter not found, install with pip install python-twitter")
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

parser.add_argument("-v","--verbose",
                    help="show more information",
                    action="store_true")

parser.add_argument("-u","--unescape",
                    help="unescape html-encoding",
                    action="store_true")

args = parser.parse_args()

#----[ Privelege Check ]------------------------------------------------------#

if os.geteuid() != 0:
    print("This script needs to be run as root.")
    sys.exit(1)

#----[ Api initialization ]---------------------------------------------------#

api = twitter.Api(consumer_key=keys.consumer_key,
                  consumer_secret=keys.consumer_secret,
                  access_token_key=keys.access_token,
                  access_token_secret=keys.access_secret)

try:
    api.VerifyCredentials()
except twitter.TwitterError as e:
    if e.message[0]['code'] == 89:
        print("Error: Invalid credentials. "
        "Make sure that your keys are stored correctly.")
        sys.exit(1)
    else:
        print("Error with authentication: code {}".format(e.message[0]['code']))
        print("Message: {}".format(e.message[0]['message']))
        sys.exit(1)
except ConnectionError as e: 
    print("Connection Error: Check your internet connection.")
    sys.exit(1)

statuses = set()
screen_name = args.screen_name

temp = [None]
oldestid = 1000000000000000000

#----[ Api call loop ]--------------------------------------------------------#

def progressbar(idnumber):
    percent = idnumber // 10000000000000000
    bars = 100 - percent
    return "[{}]\r".format(("=" * bars) + (" " * percent))

print("Beginning scan for tweets...")

if not args.verbose:
    print("Scan generally finishes before the progress bar does, "
          "depending on how long the user has been active on twitter.")

while (len(temp) > 0):

    try:
        temp = api.GetUserTimeline(screen_name=screen_name,
                                   trim_user=True,
                                   max_id=oldestid)
    except twitter.TwitterError:
        print("Request failed, retrying in 5s.")
        time.sleep(5)
        continue

    if args.verbose:
        print("Got {} tweets after id {}".format(len(temp), oldestid))
    else:
        print(progressbar(oldestid),end="")
    oldestid = min([s.id for s in temp], default=2) - 1

    for i in temp:
        statuses.add(i.text)

if not args.verbose:
    print()

print("finished!")

if args.verbose:
    print("Found a total of {} unique statuses".format(len(statuses)))

#----[ Filtering ]------------------------------------------------------------#

if args.nolinks:
    filteredstatuses = {x for x in statuses if "http" not in x}

    if args.verbose:
        text = "Filtered out {} statuses with embedded links"
        print(text.format(len(statuses) - len(filteredstatuses)))

    statuses = filteredstatuses

if args.nomentions:
    filteredstatuses = {x for x in statuses if "@" not in x}

    if args.verbose:
        text = "Filtered out {} statuses with mentions"
        print(text.format(len(statuses) - len(filteredstatuses)))
    
    statuses = filteredstatuses

if args.unescape:
    filteredstatuses = {html.unescape(x) for x in statuses}

    if args.verbose:
        text = "html de-encoded statuses"
        print(text)

    statuses = filteredstatuses

#----[ File Output ]----------------------------------------------------------#

datfile = open(screen_name, "w")

for i in statuses:
    datfile.write(i)
    datfile.write("\n%\n")

datfile.close()

#----[ Datfile Generation and Installation ]----------------------------------#

if args.verbose:
    call(["strfile", "-c", "%", datfile.name, datfile.name + ".dat"])
else:
    devnull = open(os.devnull, 'w')
    call(["strfile", "-c", "%", datfile.name, datfile.name + ".dat"],
            stdout=devnull,
            stderr=devnull)
    devnull.close()


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

if args.verbose:
    print("files installed successfully!")

print("found a total of {} tweets after filtering".format(len(statuses)))
print("use 'fortune {}' to generate fortunes".format(datfile.name))
