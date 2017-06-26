import math, requests

# Botswana, Kenya, Lesotho, Madagascar, South Africa
# Swaziland, Tanzania, Uganda
# Removed Madagascar, Tanzania: no hits
# Added Reunion, Senegal, Tunisia
AFRICA_LIST = ["BWA", "KEN", "LSO", "ZAF", "SWZ", "UGA", "REU", "SEN", "TUN"]

# Bangladesh, Bhutan, British Indian Ocean Territory, Cambodia, Hong Kong
# India, Indonesia, Israel, Japan, Jordan, Kazakhstan, Macau, Malaysia, Maldives
# Mongolia, Nepal, Palestine, Philippines, Qatar, Saudi Arabia, Singapore, 
# South Korea, Taiwan, Thailand, United Arab Emirates
# Kazahkstan, Jordan, Saudi Arabia, Vietnam, Egypt, "Qatar removed: no hits
# Kyrgyzstan, Laos, Sri Lanka added
ASIA_LIST = ["BGD", "BTN", "IOT", "KHM", "HKG", "IND", "IDN", 
"ISR", "JPN", "MAC", "MYS", "MDV", "MNG", "NPL",
"PSE", "PHL", "SGP", "KOR", "TWN", "THA", "ARE", "LKA"]

# Aland, Andorra, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark
# Estonia, Finland, France, Germany, Gibraltar, Greece, Hungary, Iceland,
# Ireland, Isle of Man, Italy, Jersey, Kosovo, Latvia, Lithuania, Luxembourg
# Macedonia, Monaco, Netherlands, Norway, Poland, Portugal, Romania, San Marino,
# Serbia, Slovakia, Spain, Sweden, Switzerland, Ukraine, United Kingdom,
# Russia, Turkey
# Error: Kosovo (UNK) not yet a country when shapefile was made?
# Removed Cyprus: no hits
# Montenegro added
EUROPE_LIST = ["ALA", "AND", "BEL", "BGR", "HRV", "CZE", 
"DNK", "EST", "FIN", "FRA", "DEU", "GIB", "GRC", "HUN", "ISL",
"IRL", "IMN", "ITA", "JEY", "LVA", "LTU", "LUX", "MKD",
"MCO", "NLD", "NOR", "POL", "PRT", "ROU", "SMR", "SRB", "SVK",
"ESP", "SWE", "CHE", "UKR", "GBR", "RUS", "TUR", "MNE"]

# Anguilla, Aruba, Belize, Bermuda, Bonaire, Canada, Curacao, Greenland,
# Guadeloupe, Martinique, Mexico, Panama, Puerto Rico, Saint Vincent and the Grenadines,
# The Bahamas, United States,
# Argentina, Bolivia, Brazil, Chile, Colombia, Ecuador, Falkland Islands,
# Peru, Uruguay, Antarctica
# Bonaire not found by shapefile, Curacao not found by shapefile
# Belize, Greenland, the Bahamas, Turks and Caicos Islands, 
# South Georgia and the South Sandwich Islands removed, no hits
# Guatemala, US Virgin Islands added
AMERICAS_LIST = ["AIA", "ABW", "BMU", "CAN",
"GLP", "MTQ", "MEX", "PAN", "PRI", "VCT", "USA",
"ARG", "BOL", "BRA", "CHL", "COL", "ECU", "FLK", "PER", "URY", "ATA", "GTM", "VIR"]

# American Samoa, Australia, East Timor, Guam,
# New Zealand, Northern Mariana Islands, 
# Error: Midway Islands deleted from ISO codes, East Timor not found
# Removed Cook Islands, Pitcairn Islands, Solomon Islands: no hits
# Vanuatu added
OCEANIA_LIST = ["ASM", "AUS", "GUM", "NZL", "MNP", "VUT"]



# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# http://www.ariel.com.au/a/python-point-int-poly.html
def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# Find area of given coordinate of a bounding box (in sq. km)
# http://mathforum.org/library/drmath/view/63767.html
def bbox_area(lat1, lon1, lat2, lon2):
    R = 6371
    lat1rad, lat2rad = math.radians(lat1), math.radians(lat2)
    lat_area = 2 * math.pi * pow(R, 2) * (abs(math.sin(lat1rad) - math.sin(lat2rad)))
    area = lat_area * (abs(lon1 - lon2) / 360)

    return area

def getCountryArea(alpha3Code, lat1, lon1, lat2, lon2):
    try:
        url = "http://restcountries.eu/rest/v1/alpha?codes=" + alpha3Code.upper()
        response = requests.get(url)
        if response.json()[0]["area"] == None:
            return bbox_area(lat1, lon1, lat2, lon2)
        else:
            return response.json()[0]["area"]
    except Exception as e:
        print "API call failed...Reverting to bounding box estimate"
        return bbox_area(lat1, lon1, lat2, lon2)



# if __name__ == "__main__":
#     print getCountryArea("SRB", 18.81702, 41.855827, 23.004997, 46.181389)
#     #print bbox_area(18.81702, 41.855827, 23.004997, 46.181389)
