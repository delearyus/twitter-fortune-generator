#!/usr/bin/env python

import sys

print("This program requires a keys.py file. Keys can be obtained from the twitter API page.")
print("Due to the nature of this program, you must register it as your own app to use it.")
print("This can be done at apps.twitter.com, and keys can then be found under 'keys and access tokens'")
print("These keys are stored locally and are not transmitted in any way.")

consumer_key = input("Consumer Key: ")
consumer_secret = input("Consumer Secret: ")
access_token = input("Access Token: ")
access_secret = input("Access Token Secret: ")

config = open("keys.py", "w")

config.write("#!/usr/bin/env python\n\n")
config.write("access_token = '{}'\n".format(access_token))
config.write("access_secret = '{}'\n\n".format(access_secret))
config.write("consumer_key = '{}'\n".format(consumer_key))
config.write("consumer_secret = '{}'\n".format(consumer_secret))

config.close()
