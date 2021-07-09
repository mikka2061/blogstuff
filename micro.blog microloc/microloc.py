#!python3
'''
Mikka is <mikka@mikka.is> - more at https://mikka.is
I am a physician, not a coder, so my code always sucks by design, just like my handwriting

- Set your 'MICROBLOG_KEY' to an App token in microblog (https://micro.blog/account/apps)
- Set your W3W_API key to a what3words API key (https://what3words.com/public-api)
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

MICROBLOG_KEY = ''
W3W_API = ''

import location
import time
import console
import photos
from random import random
import what3words
import base64
import json                    
import requests

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
	'''
	makes and returns the map image. still no error checking, because YOLO
	'''
	
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
	filename = w3w["words"] + ".jpg"
	with open(filename, 'wb') as f:
		f.write(jpeg_data)
	return [filename, w3w["words"]]

def post_image(image_file):
	link = "https://micro.blog/micropub?q=config"
	f = requests.get(link)
	me = json.loads(f.text)['media-endpoint']
	header = {'Authorization' : 'Bearer {}'.format(MICROBLOG_KEY)}
	files = {'file':(image_file, open(image_file, 'rb'))}
	r = requests.post(me, headers=header, files=files, verify=False)
	imgurl = json.loads(r.text)['url']
	return imgurl

def make_post(imgurl, w3words):
	mytext = "Aerial view of my current or recent location at <a href='https://w3w.co/{}'>w3w://{}</a>".format(w3words,w3words)
	header = {'Authorization' : 'Bearer {}'.format(MICROBLOG_KEY)}
	data = {'h': 'entry', 'content': mytext, 'photo': imgurl}
	# h=entry&content=Hello%20world.&photo=https://...&mp-photo-alt=Description%20here.
	r = requests.post("https://micro.blog/micropub", headers=header, data=data, verify=False)	

def main():
	image_file, w3words = make_img()
	imgurl = post_image(image_file)
	make_post(imgurl, w3words)
	exit()

if __name__ == '__main__':
	main()