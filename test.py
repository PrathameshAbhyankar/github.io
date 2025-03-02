import socket
import os
import time
from threading import Thread


import socket
import time
import datetime

import geocoder
from geopy.geocoders import Nominatim

g = geocoder.ip('me')
print(g.latlng)
    #geoLoc = Nominatim(user_agent="GetLoc")
lattlongStringArray = g.latlng
lattLongString = str(lattlongStringArray[0]) + "," + str(lattlongStringArray[1]) 

print(lattLongString)

