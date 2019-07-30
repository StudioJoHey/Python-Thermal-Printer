#!/usr/bin/python

# This is a Python port of Adafruit's "Gutenbird" sketch for Arduino.
# Polls one or more Twitter accounts for changes, displaying updates
# on attached thermal printer.
# Written by Adafruit Industries.  MIT license.
#
# Required hardware includes an Internet-connected system with Python
# (such as Raspberry Pi) and an Adafruit Mini Thermal Receipt printer
# and all related power supplies and cabling.
# Required software includes Adafruit_Thermal and PySerial libraries.
#
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack
#
# Uses Twitter 1.1 API application-only authentication.  This
# REQUIRES a Twitter account and some account configuration.  Start
# at dev.twitter.com, sign in with your Twitter credentials, select
# "My Applications" from the avatar drop-down menu at the top right,
# then "Create a new application."  Provide a name, description,
# placeholder URL and complete the captcha, after which you'll be
# provided a "consumer key" and "consumer secret" for your app.
# Copy these strings to the globals below, and configure the search
# string to your liking.  DO NOT SHARE your consumer key or secret!
# If you put code on Github or other public repository, replace them
# with dummy strings.
#
# Adopted by Studio JoHey to experiment for digital-analog exchange
# in the public urban sphere--> studio-johey.de
# Runs on Python 3 and related libraries

from __future__ import print_function
from html.parser import HTMLParser
import base64, http.client, json, sys, urllib.parse, urllib.request, zlib,  \
       subprocess, time, socket
from Adafruit_Thermal import *

from PIL import Image


# Configurable globals.  Edit to your needs. -------------------------------

# Twitter application credentials -- see notes above -- DO NOT SHARE.
consumer_key    = 'PUT_YOUR_CONSUMER_KEY_HERE'
consumer_secret = 'PUT_YOUR_CONSUMER_SECRET_HERE'

bearer_token = base64.b64encode('{}:{}'.format(
    consumer_key, consumer_secret).encode('utf8'))

# queryString can be any valid Twitter API search string, including
# boolean operators.  See http://dev.twitter.com/docs/using-search
# for options and syntax.  Funny characters do NOT need to be URL
# encoded here -- urllib takes care of that.
#queryString = 'from:W_SK include_entities=true'
queryString2 = "%23nordendof&include_entities=true"


# Other globals.  You probably won't need to change these. -----------------

printer   = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)
host      = 'api.twitter.com'
authUrl   = '/oauth2/token'
searchUrl = '/1.1/search/tweets.json?'
agent     = 'Gutenbird v1.0'

# lastID is command line value (if passed), else 1
if len(sys.argv) > 1: lastId = sys.argv[1]
else: lastId = '1'
#lastId = '1131332578047406081' #TEST ID! after which there should be nthng
#lastId = '1'

# Initiate an HTTPS connection/request, uncompress and JSON-decode results
def issueRequestAndDecodeResponse(method, url, body, headers):
  connection = http.client.HTTPSConnection(host)
  connection.request(method, url, body, headers)
  response = connection.getresponse()
  if response.status != 200:
    # This is OK for command-line testing, otherwise
    # keep it commented out when using main.py
    # print('HTTP error: %d' % response.status)
    exit(-1)
  compressed = response.read()
  connection.close()
  json_token = zlib.decompress(compressed, 16+zlib.MAX_WBITS)
  return json.loads(json_token.decode('utf-8'))


# Mainline code. -----------------------------------------------------------

# Get access token. --------------------------------------------------------

token = issueRequestAndDecodeResponse(
  'POST', authUrl, 'grant_type=client_credentials',
   {'Host'            : host,
    'User-Agent'      : agent,
    'Accept-Encoding' : 'gzip',
    'Content-Type'    : 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization'   : 'Basic {0}'.format(bearer_token.decode('utf-8'))}
  )['access_token']


# Perform search. ----------------------------------------------------------

data = issueRequestAndDecodeResponse(
  'GET',
  (searchUrl + 'count=3&since_id=%s&q=%s' %
   (lastId, queryString2)),
  None,
  {'Host'            : host,
   'User-Agent'      : agent,
   'Accept-Encoding' : 'gzip',
   'Authorization'   : 'Bearer ' + token})

#print(data)

# Display results. ---------------------------------------------------------

maxId = data['search_metadata']['max_id_str']

for tweet in data['statuses']:

  printer.underlineOn()
  printer.print('{:<31}'.format(tweet['user']['screen_name'])+' auf Twitter unter #NordendOF')
  printer.underlineOff()
  
  printer.feed(1)

  printer.print('{:<32}'.format(tweet['created_at']))
  
  printer.feed(2)

  if 'extended_entities' in tweet:
    getpic = tweet['extended_entities']['media'][0]['media_url']
    pic = Image.open(urllib.request.urlopen(getpic))
    basewidth = 400
    wpercent = (basewidth / float(pic.size[0]))
    hsize = int((float(pic.size[1]) * float(wpercent)))
    img = pic.resize((basewidth, hsize), Image.ANTIALIAS)
    printer.printImage(img, True)

  # Remove HTML escape sequences
  # and remap Unicode values to nearest ASCII equivalents
  printer.print(
    HTMLParser().unescape(tweet['text'])+ '\n\nDein Kommentar:\n' +
'\n................................' +
#'\n\n...............................' +
#'\n\n...............................' +
'\n\n...............................\n' + ' ')

  # max_id_str is not always present, so check tweet IDs as fallback
  id = tweet['id_str']
  if(id > maxId): maxId = id # String compare is OK for this

  printer.feed(3)


print(maxId) # Piped back to calling process
