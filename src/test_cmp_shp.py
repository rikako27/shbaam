#!/usr/bin/env python3
#test_cmp_shp.py

#Compare two shapefiles
#1. Check the geometries
#2

import sys
import fiona


len_arg = len(sys.argv)
if len_arg != 3:
    print("Error -- only 2 arguments can be used")
    raise SystemExit(22)

old_shp = sys.argv[1]
new_shp = sys.argv[2]

#print command line inputs
print("Command Line Inputs")
print(' shapefile 1: ' + old_shp)
print(' shapefile 2: ' + new_shp)
print("--------------------------------------------------")
try:
    with open(old_shp) as file:
        pass
except IOError as e:
    print("Unable to open " + shp)
    raise SystemExit(22)

try:
    with open(new_shp) as file:
        pass
except IOError as e:
    print("Unable to open " + shp)
    raise SystemExit(22)
print("input files exist")

#Open old_shp
print("Open old_shp")
old_pf = fiona.open(old_shp, 'r')
old_total = len(old_pf)
print("-- The number of features is: " + str(old_total))
old_property = old_pf.schema["properties"].keys()
print("-- The number of attributes is: " + str(len(old_property)))

#Open new_shp
print("Open new_shp")
new_pf = fiona.open(new_shp, 'r')
new_total = len(new_pf)
print("-- The number of features is: " + str(new_total))
new_property = new_pf.schema["properties"].keys()
print("-- The number of attributes is: " + str(len(new_property)))

print("Compare number of features")
if old_total == new_total:
    print("-- The number of features are the same")
else:
    print("Error -- the numbers of features are different "+
    str(old_total) + " <> " + str(new_total))
    raise SystemExit(99)

print("Compare contents of shapefiles")
for p in range(old_total):
    #get the properties and geometry for the current feature of old file
    old_point = old_pf[p]
    old_prop = old_point["properties"]
    old_geo = old_point["geometry"]

    #get the properties and geometry for the current feature of new file
    new_point = new_pf[p]
    new_prop = new_point["properties"]
    new_geo = new_point["geometry"]

    #Compare geometry
    if old_geo != new_geo:
        print("Error - the geometries of features are different for index: "
        + str(p))
        raise SystemExit(99)

    #Compare attributes
    for prop in old_property:
        if old_prop[prop] != new_prop[prop]:
            print("Error - The attributes of features are different for index: "
            + str(p) + ", attribute: " + str(prop))
            raise SystsemExit(99)
print("Success!")
