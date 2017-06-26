street view scraper
========

Command-line Python script to get Google Street View images from random locations around the world.
Inspired and modified from a similar <a href="https://github.com/hugovk/random-street-view">library</a>

High level logic:
-----------------
1. Random (lat, lon) coordinates are generated from the country's border's bounding box
2. Coordinates are checked to make sure they're within the actual borders
3. Coordinates are checked using a "hidden" (not publicly exposed) Google API that will pull the nearest Street View. Often there is no imagery for the location, so the . Repeat until required number of images have been fetched.

You can see <a href="http://support.google.com/maps/bin/answer.py?hl=en&answer=68384">Street View coverage here</a>.

Prerequisites
-------------

 * To be filled in

Usage
-----

    usage: random_street_view.py [-cont] continent

    Get random Street View images from a given continent

For example:

    python random_street_view.py AFRICA
