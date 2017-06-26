import argparse
import os
import math
import random
import shapefile  # pip install pyshp
import sys
import urllib
import geoutils
import time
import streetview
import numpy as np
import streetview_writer as sv_writer
from numpy.random import choice
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClient
from tornado import gen

# Google Street View Image API
# 25,000 image requests per 24 hours
# See https://developers.google.com/maps/documentation/streetview/
API_KEY = "AIzaSyCHkdjGuWGJtWFKQTUrlrmtxEtTSH8Eu28"
GOOGLE_URL = ("http://maps.googleapis.com/maps/api/streetview?sensor=false&" +
			  "size=300x300&key=" + API_KEY)
CONT_LIST = []
CONT_WEIGHT_LIST = [0.29, 0.17, 0, 0.29, 0.25]
CONT_COUNTRY_WEIGHT_LIST = []
COUNTRY_TO_AREA = {}
attempts, continent_hits, imagery_hits, imagery_misses = 0, 0, 0, 0
country_count_map = {}
OUTFILE = "streetviews.txt"

def getBalanceFactor(country_name):
	# percentCountry = db.getPercentageofCountry(country_name)
	# if percentCountry == 0:
	#     balancefactor = 5
	balancefactor = 1
	percentCountry = sv_writer.getPercentageofCountry(country_name)

	# Normal algorithm
	if percentCountry == 0:
		balancefactor = 2
	elif percentCountry < 0.005:
		balancefactor = 5
	elif percentCountry > 0.03:
		balancefactor = 0
	else:
		balancefactor = (1/float(100)) / percentCountry
		#balancefactor = (1/float(92)) / percentCountry
	return balancefactor

def build_world_shapes():
	print "Getting continent"
	for continent in CONT_LIST:
		country_shapes = []
		for country in continent:
			found_flag = False
			for i, record in enumerate(sf.records()):
				if record[2] == country:
					print "Added: " + record[2], record[4]
					country_shapes.append(shapes[i]) # Add each country shape to country shape list
					country_area = geoutils.getCountryArea(record[2], shapes[i].bbox[0], 
						shapes[i].bbox[1], shapes[i].bbox[2], shapes[i].bbox[3])
					COUNTRY_TO_AREA[country] = country_area # Add each country area to dictionary
					print "Area of country: " + str(country_area)
					found_flag = True
					break
			if not found_flag:
				print "Error: cannot find country " + country
				sys.exit()
		# Add country shape list to continent shape list
		world_shapes.append(country_shapes)   

def init_parser():
	parser = argparse.ArgumentParser(
		description="Get random Street View images from a given country or continent",
			formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument(
		'-n', '--images-wanted', type=int,
		default=1000,
		help="Number of images wanted")
	parser.add_argument(
		'-cont', '--continent',
		help="Specify which continent you want to target (Africa, Asia, Europe, Americas, Oceania")
	parser.add_argument('-o', '--outfile', help='the file to save captured streetviews')

	return parser


def parse_args(parser):
	args = parser.parse_args()

	global CONT_LIST
	if args.continent:
		if args.continent.upper() == "AFRICA":
			CONT_LIST = geoutils.AFRICA_LIST
		elif args.continent.upper() == "ASIA":
			CONT_LIST = geoutils.ASIA_LIST
		elif args.continent.upper() == "EUROPE":
			CONT_LIST = geoutils.EUROPE_LIST
		elif args.continent.upper() == "AMERICAS":
			CONT_LIST = geoutils.AMERICAS_LIST
		elif args.continent.upper() == "OCEANIA":
			CONT_LIST = geoutils.OCEANIA_LIST
		else:
			print "Error: Incorrect continent specified"
			sys.exit()
	else:
		CONT_LIST = [geoutils.AFRICA_LIST, geoutils.ASIA_LIST, geoutils.EUROPE_LIST, geoutils.AMERICAS_LIST, geoutils.OCEANIA_LIST]

	global outfile
	if args.outfile:
		OUTFILE = args.outfile


def init_country_weights():
	country_weight_list = []
	
	for cont in CONT_LIST:
		cont_list = []
		total = 0
		for country in cont:
			weight = int(math.sqrt(COUNTRY_TO_AREA[country]))/5 * getBalanceFactor(country)
			total+=weight
			#print country, str(weight)
			cont_list.append(weight)
		cont_list[:] = [(x/float(total)) for x in cont_list]
		country_weight_list.append(cont_list)


	for i in range(len(country_weight_list)):
		print "###############################"
		for j in range(len(country_weight_list[i])):
			print CONT_LIST[i][j], str(country_weight_list[i][j])

	return country_weight_list

@gen.coroutine
def get_streetview_async():
	global attempts
	attempts+=1
	continent_idx = choice(np.arange(len(CONT_LIST)), p=CONT_WEIGHT_LIST)
	#country_idx = int(random.uniform(0, len(CONT_LIST[continent_idx])))
	country_idx = choice(np.arange(len(CONT_LIST[continent_idx])), p=CONT_COUNTRY_WEIGHT_LIST[continent_idx])
	country_name = CONT_LIST[continent_idx][country_idx]
	country_shape = world_shapes[continent_idx][country_idx]


	if country_name in country_count_map:
		country_count_map[country_name]+=1
	else:
		country_count_map[country_name] = 1

	min_lon = country_shape.bbox[0]
	min_lat = country_shape.bbox[1]
	max_lon = country_shape.bbox[2]
	max_lat = country_shape.bbox[3]
	borders = country_shape.points

	print "SWITCHING TO COUNTRY: " + country_name
	outfile = os.path.join(OUTFILE)
	
	# Get a random (lat,lon)
	rand_lat = round(random.uniform(min_lat, max_lat), 6)
	rand_lon = round(random.uniform(min_lon, max_lon), 6)
	# Is (lat,lon) inside borders?
	if geoutils.point_in_polygon(rand_lon, rand_lat, borders):
		global continent_hits
		continent_hits+=1
		lat_lon = str(rand_lat) + "," + str(rand_lon)
		url = GOOGLE_URL + "&location=" + lat_lon

		#panoids = yield streetview.panoids_async(lat=rand_lat, lon=rand_lon)
		has_street_view = yield streetview.has_streetview_async(lat=rand_lat, lon=rand_lon)
		#if panoids:
		if has_street_view:
			# Write street view details to file
			with open(outfile, "a") as myfile:
				myfile.write(str(rand_lat) + "\t" + str(rand_lon) + "\t" + str(country_name) + "\n")
				print "\t========== Got one! =========="
			global imagery_hits
			imagery_hits+=1
		else:
			global imagery_misses
			imagery_misses+=1



if __name__ == "__main__":
	parser = init_parser()
	parse_args(parser)

	print "Loading borders"
	shape_file = "shapefiles/TM_WORLD_BORDERS-0.3.shp"
	if not os.path.exists(shape_file):
		print("Cannot find " + shape_file + ". Please download it from "
			  "http://thematicmapping.org/downloads/world_borders.php "
			  "and try again.")
		sys.exit()

	sf = shapefile.Reader(shape_file)
	shapes = sf.shapes()


	#Build list of continent shapes
	world_shapes = []
	build_world_shapes()

	#Set probability weights for each country
	global CONT_COUNTRY_WEIGHT_LIST
	CONT_COUNTRY_WEIGHT_LIST = init_country_weights()
		
	print "Getting images"	    

	try:
		PeriodicCallback(get_streetview_async, 10).start()
		IOLoop.instance().start()

	except KeyboardInterrupt:
		print "Keyboard interrupt"

	global country_count_map
	for key, value in country_count_map.iteritems():
		print key, value

	print "Attempts:\t", attempts
	print "Continent hits:\t", continent_hits
	print "Imagery misses:\t", imagery_misses
	print "Imagery hits:\t", imagery_hits

# End of file


