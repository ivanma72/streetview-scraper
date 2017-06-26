"""
Module that integrates with the official Google Street View Metadata API
"""

import requests
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import json

BASE_URL = "https://maps.googleapis.com/maps/api/streetview/metadata?"
API_KEY = "AIzaSyBcD2rLh01Z5QOnZNCHBVmv2zvLCCtFbkU"

@gen.coroutine
def has_streetview_async(lat, lon):
	url = BASE_URL + "location={0},{1}&key={2}"
	formatted_url = url.format(lat, lon, API_KEY)
	#async call to API
	response = yield AsyncHTTPClient().fetch(formatted_url)
	
	#parse response
	json_response = json.loads(response.body)
	status = json_response["status"]
	if(status == "OK"):
		raise gen.Return(True)
	else:
		print "No streetview found: " + status
		raise gen.Return(False)


def has_streetview(lat, lon):
    url = BASE_URL + "location={0},{1}&key={2}"
    formatted_url = url.format(lat, lon, API_KEY)
    #sync call to API
    response = requests.get(formatted_url)
    
    #parse response
    json_response = response.json()
    status = json_response["status"]
    if(status == "OK"):
        return True
    else:
        return False