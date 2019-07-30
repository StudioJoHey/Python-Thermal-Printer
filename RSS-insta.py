import feedparser
import urllib.request
import io
import sys
from operator import itemgetter
from PIL import Image
import serial
import locale
import time

from Adafruit_Thermal import *
printer = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)

#locale.setlocale(locale.LC_ALL, 'de_DE')

#instaNord_rss_url = "http://fetchrss.com/rss/5c67e7af8a93f80e478b45675c69ddae8a93f8da068b4567.xml"
instaOF_rss_url = "http://fetchrss.com/rss/5ce6de1a8a93f8f1528b45675ce6de9d8a93f82b568b4568.xml"

if len(sys.argv) > 1:
    lastPostDate = time.strptime(sys.argv[1], "%d.%m.%Y_%H:%M:%S")
else:
    lastPostDate = time.strptime("01.01.2019_00:00:00",
                                 "%d.%m.%Y_%H:%M:%S")

#Sort Feed by date published, [0] = most recent item
NewsFeed = feedparser.parse(instaOF_rss_url)
unsortedFeedEntries = NewsFeed['entries']
sortedFeedEntries = sorted(unsortedFeedEntries,
    key=itemgetter('published_parsed'), reverse=True)

# set last Post and rebuild it to fit same build time as piped time
# (which does not have to have the same DST value as the RSS import)
lastPost = sortedFeedEntries[0]
postDate = lastPost['published_parsed']
postDateStr = str(time.strftime("%d.%m.%Y_%H:%M:%S", postDate))
postDate = time.strptime(postDateStr,
                                 "%d.%m.%Y_%H:%M:%S")

if postDate > lastPostDate:
    #get and scale post image for printer roll
    lastPostImgScaled = None

    lastPostImgLink = lastPost['media_content'][0]['url']
    lastPostImgFile = io.BytesIO(urllib.request.urlopen(lastPostImgLink).read())
    lastPostImg = Image.open(lastPostImgFile)

    basewidth = 400
    wpercent = (basewidth / float(lastPostImg.size[0]))
    hsize = int((float(lastPostImg.size[1]) * float(wpercent)))
    lastPostImgScaled = lastPostImg.resize((basewidth, hsize), Image.ANTIALIAS)

    # Print last feed, starting with source
    printer.underlineOn()
    printer.print("Letzter Post von \n" + NewsFeed.feed['title'])
    printer.underlineOff()

    printer.print('\n ' + lastPost.published[0:-5] + '\n' + '\n')

    if lastPostImgScaled != None:
        printer.printImage(lastPostImgScaled, True)

    lastPostTextContent = lastPost.summary_detail['value']
    TextSectionMarkerIn = lastPostTextContent.find('<br/>')
    TextSectionMarkerOut = lastPostTextContent.find('<br />')
    lastPostText = lastPostTextContent[TextSectionMarkerOut+6:-1]
    printer.print(lastPostText)
    
    printer.feed(2)

    printer.print(
    '\nDein Kommentar:\n' +
    '\n................................' +
    '\n\n...............................' +
    '\n\n...............................\n' + ' ' + ' \n ')
    
    printer.feed(3)
    lastPostDate = postDate

lastPostDateStr = str(time.strftime("%d.%m.%Y_%H:%M:%S", lastPostDate))

print(lastPostDateStr) # Piped back to calling process


