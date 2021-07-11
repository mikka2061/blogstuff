#!python3

import location
import time
import photos
import what3words
import json                    
import requests
import os
from urllib.parse import quote

'''
Mikka is <mikka@mikka.is> - more at https://mikka.is

I am a physician, not a coder, so my code always sucks by design, just like my handwriting
- Set your 'MICROBLOG_KEY' to an App token in microblog (https://micro.blog/account/apps)
- Set your W3W_API key to a what3words API key (https://what3words.com/public-api)
- See the other options, they might be useful
- **ESPECIALLY** check out MAKE_DRAFT
- Install Pythonista 3 (https://omz-software.com/pythonista/) on your iPhone, M1 Mac, or iPad
- Save this file somewhere in your iCloud
- Install StaSH inside Pythonista (https://github.com/ywangd/stash)
- Run StaSH and install what3words (`pip install what3words`)
- open the iCloud saved file
- I am writing image files to that directory. Clean them out occassionally.

Problems:
- once in a while location.render_map_snapshot returns an empty object. Largely due to CoreLocation issues
- there is NO error checking, add your own or YOLO it
- requests.packages.urllib3.disable_warnings() is on for me, because I run a Beta of iOS where SSL verification is BS broken. Turn it off, if you can.
'''

# This one here is important. Set it to make the post a Draft, which you can then edit in the iOS or Mac app.
# This allows you to snapshot your aerial view, save it to Photos (if desired), and then edit the text later,
# adding pithy observations.
MAKE_DRAFT = True

# And this one is confusing :)
# If you have installed or are using the Drafts app (https://getdrafts.com) you can opt
# to not post the entry but have it sent to Drafts, so you can keep editing it. The image
# will be uploaded, and then a new Draft in Drafts will be opened. Send this to micro.blog
# with the according built in Drafts action (see https://actions.getdrafts.com/a/1Hg)
SEND_DRAFT = False

# Set your key from micro.blog here (https://micro.blog/account/apps)
MICROBLOG_KEY = ''

# Get a what3words API key (see README.md)
W3W_API = ''

# Want to also create a cool timeline of aerial views in Photos.app? Create an album and
# set this to True and to the name of the Album. Totally cool. Also really useful if you
# have a Day One diary and want to illustrate your daily diaries.
SAVE_TO_ALBUM = True
ALBUM_NAME = ""

# NOT a big fan of this, but for iOS Beta it needs to be set
requests.packages.urllib3.disable_warnings()


def getplace_w3w(lat, lon):
  geocoder = what3words.Geocoder(W3W_API)
  return (geocoder.convert_to_3wa(what3words.Coordinates(lat, lon)))


def get_location():
  location.start_updates()
  time.sleep(2)
  myloc = location.get_location()
  location.stop_updates()
  return myloc

def make_img():
  # makes and returns the map image. still no error checking, because YOLO
  loc = get_location()
  w3w = getplace_w3w(loc["latitude"], loc["longitude"])	

  img = location.render_map_snapshot(
    loc['latitude'],
    loc['longitude'],
    width=1000,
    height=1000,
    img_width=1000,
    img_height=1000,
    map_type='hybrid')

  jpeg_data = img.to_jpeg()
  filename = os.path.expanduser("~/Documents") + "/" + w3w["words"] + ".jpg"

  with open(filename, 'wb') as f:
    f.write(jpeg_data)
  return [filename, w3w["words"], loc]


def post_image(image_file):
	link = "https://micro.blog/micropub?q=config"
	f = requests.get(link)
	me = json.loads(f.text)['media-endpoint']
	header = {'Authorization': 'Bearer {}'.format(MICROBLOG_KEY)}
	files = {'file': (image_file, open(image_file, 'rb'))}
	r = requests.post(me, headers=header, files=files, verify=False)
	imgurl = json.loads(r.text)['url']
	return imgurl


def image_to_albums(imagefile, w3words, loc):
  asset = photos.create_image_asset(imagefile)
  asset.location = {
    'latitude': loc['latitude'],
    'longitude': loc['longitude'],
    'altitude': loc['altitude']	
  }
  album = [xx for xx in photos.get_albums() if xx.title == ALBUM_NAME][0]
  x = album.add_assets([asset])
  

def make_post(imgurl, w3words):
  mytext = "Aerial view of my current or recent location at <a href='https://w3w.co/{}'>w3w://{}</a>".format(w3words,w3words)
  header = {'Authorization': 'Bearer {}'.format(MICROBLOG_KEY)}
  data = {'h': 'entry', 'content': mytext, 'photo': imgurl}
  if SEND_DRAFT:
    import clipboard
    import webbrowser
    text = mytext + "\n" + "<img src='{}' alt='aerial view of {}'/>".format(imgurl, w3words)
    webbrowser.open("drafts://x-callback-url/create?text={}".format(quote(text)))
    return
    
  if MAKE_DRAFT:
    data['post-status'] = 'draft'

  requests.post("https://micro.blog/micropub", headers=header, data=data, verify=False)	


def main():
  image_file, w3words, loc = make_img()
  imgurl = post_image(image_file)
  if SAVE_TO_ALBUM:
    image_to_albums(image_file, w3words, loc)
    make_post(imgurl, w3words)
  os.remove(image_file)
  exit()

if __name__ == '__main__':
	main()
