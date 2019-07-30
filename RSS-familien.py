import feedparser
import urllib.request
from operator import itemgetter
import io
import sys
from PIL import Image
import serial

from Adafruit_Thermal import *
printer = Adafruit_Thermal("/dev/serial0", 9600, timeout=5)

familien_rss_url = "https://www.familien-blickpunkt.de/aktuelles/rss/index.php?keyword=nordend"

if len(sys.argv) > 1:
    lastPostDate = time.strptime(sys.argv[1], "%d.%m.%Y_%H:%M:%S")
else:
    lastPostDate = time.strptime("01.01.2019_00:00:00",
                                 "%d.%m.%Y_%H:%M:%S")

#Sort Feed by date published, [0] = most recent item
NewsFeed = feedparser.parse(familien_rss_url)
unsortedFeedEntries = NewsFeed['entries']
sortedFeedEntries = sorted(unsortedFeedEntries,
    key=itemgetter('published_parsed'), reverse=True)

# set last Post and rebuild it to fit same build time as piped time
# (which does not have to have the same DST value as the RSS import)
lastPost = sortedFeedEntries[0]
postDate = lastPost['published_parsed']
postDateStr = str(time.strftime("%d.%m.%Y_%H:%M:%S", postDate))
postDate = time.strptime(postDateStr, "%d.%m.%Y_%H:%M:%S")

if postDate > lastPostDate:
#get and scale post image for printer roll
    lastPostImgScaled = None
    if 'img_src' in lastPost:
        lastPostImgLink = lastPost['img_src']
        #fake Agent to avoid 403 - forbidden message from python agent
        req = urllib.request.Request(lastPostImgLink, headers={'User-Agent': 'Mozilla/5.0'})
        lastPostImgFile = io.BytesIO(urllib.request.urlopen(req).read())
        lastPostImg = Image.open(lastPostImgFile)

        basewidth = 300
        wpercent = (basewidth / float(lastPostImg.size[0]))
        hsize = int((float(lastPostImg.size[1]) * float(wpercent)))
        lastPostImgScaled = lastPostImg.resize((basewidth, hsize), Image.ANTIALIAS)


    # Print last feed, starting with source
    printer.underlineOn()
    #printer.inverseOn()
    printer.print("" + NewsFeed.feed['title'])
    #printer.inverseOff()
    printer.underlineOff()

    printer.print(lastPost.published[0:-6] + '\n' + '\n')

    if lastPostImgScaled != None:
        printer.printImage(lastPostImgScaled, True)

    printer.underlineOn()
    printer.print(lastPost.title + '\n')
    printer.underlineOff()
    printer.print(lastPost.summary_detail['value'] + '\n')

    printer.print(
    '\nDein Kommentar:\n' +
    '\n................................' +
    '\n\n...............................' +
    '\n\n...............................\n' + ' ' + ' \n ')
    
    printer.feed(3)
    lastPostDate = postDate

lastPostDateStr = str(time.strftime("%d.%m.%Y_%H:%M:%S", lastPostDate))

print(lastPostDateStr) # Piped back to calling process
