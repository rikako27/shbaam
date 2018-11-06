import fiona
import sys
from netCDF4 import Dataset
import shapely.geometry
import shapely.prepared
import rtree
import numpy
import math

#1 -- nc4_file
#2 -- shape_filei
#nc4_file = sys.argv[1]
#shape_file = sys.argv[2]
nc4_file = '../src/output1.nc4'
#shape_file = '../input/SERVIR_STK/NorthWestBD.shp'
shape_file = '../input/SERVIR_STK/Nepal.shp'
point_file = '../output/SERVIR_STK/GLDAS.VIC.pnt_tst.shp'


#Open netCDF4 file
nc4 = Dataset(nc4_file, 'r', format="NETCDF4")

#Read polygon shapefile
pol = fiona.open(shape_file, 'r')

#Create a point shapefile with all GLDAS grid cells
point_driver = pol.driver
point_crs = pol.crs

point_schema = {'geometry': 'Point',
             'properties': {'lon' : 'float',
                            'lat' : 'float',
                            }}

with fiona.open( point_file, 'w', driver=point_driver, crs=point_crs, schema=point_schema) as pf:
   for lon_index in range(len(nc4.dimensions['lon'])):
        longitude = nc4.variables['lon'][lon_index]

        for lat_index in range(len(nc4.dimensions['lat'])):
            latitude = nc4.variables['lat'][lat_index]

            pf_property = { 'lon': longitude, 'lat': latitude }
            pf_geometry = shapely.geometry.mapping(
                        shapely.geometry.Point((longitude, latitude)))
            pf.write({
                       'properties': pf_property,
                       'geometry': pf_geometry,
                     })

print('Success -- created a new shapefile')

#Create spatial index for the bounds of each point feature
idx = rtree.index.Index()

#Open new shapefile
pf = fiona.open(point_file, 'r')
for point in pf:
    point_id = int(point['id'])
    point_bounds = shapely.geometry.shape(point['geometry']).bounds
    idx.insert(point_id, point_bounds)

#Find grid cells that intersect with polygon
total = 0
interest_lon = []
interest_lat = []

for polygon in pol:
    polygon_geo = shapely.geometry.shape(polygon['geometry'])
    prepared_polygon = shapely.prepared.prep( polygon_geo )
    for pf_id in [int(i) for i in list(idx.intersection(polygon_geo.bounds))]:
        point = pf[pf_id]
        point_bounds = shapely.geometry.shape(point['geometry'])
        if prepared_polygon.contains(point_bounds):
            print('cell:', pf_id)
            interest_lon.append( point['properties']['lon'] )
            interest_lat.append( point['properties']['lat'] )
            total += 1

print('The total cells found: ' + str(total) )
print('The longitude of the cells: ' + str(interest_lon) )
print('The lattitude of the cells: '+ str(interest_lat) )


#Find long-term mean for each intersecting GRACE grid cell
print('Find long-term mean for each intersecting GRACE grid cell')
time_steps = len(nc4.dimensions['time'])

lat_indices = []
lon_indices = []
for index in range(total):
	lon_indices.append((nc4["lon"][:]).tolist().index(interest_lon[index]))
	lat_indices.append((nc4["lat"][:]).tolist().index(interest_lat[index]))


intersect_avg = [0.0] * total
for cell_index in range( total ):
    lon = lon_indices[ cell_index ]
    lat = lat_indices[ cell_index ]
    for time in range(time_steps):
        print(time, lon, lat)
        print(nc4.variables['SWE'][time, lat, lon])
        intersect_avg[ cell_index ] = intersect_avg[ cell_index ] + \
                                    nc4.variables['SWE'][time, lat, lon]

intersect_avg = [i / time_steps for i in intersect_avg]
print('long-term mean:', intersect_avg)


#Compute surface area of each grid cell
print('Compute surface area of each grid cell')

longitude_step_size = abs(nc4["lon"][1]-nc4["lon"][0])
latitude_step_size = abs(nc4["lat"][1]-nc4["lat"][0])

area = [0] * total

for lat_index in range(len(lat_indices)):
    lat = nc4['lat'][ lat_indices[lat_index] ]
    area[ lat_index ] = 6371000*math.radians(latitude_step_size) \
                                *6371000*math.radians(longitude_step_size)\
                                *math.cos(math.radians(lat))

total_area = sum(area)
print('total_area: ', total_area)
#Now compute SWE storage anomaly timeseries
print()
print('Compute SWE storage anomaly timeseries')
anomalies = []

for time in range(time_steps):
    anomaly_in_time = 0
    for cell_index in range(total):
        lon_index = lon_indices[cell_index]
        lat_index = lat_indices[cell_index]
        areaa = area[cell_index]
        long_term_mean = intersect_avg[cell_index]

        anomaly_in_area = ( nc4.variables['SWE'][time, lat_index, lon_index] \
                            - long_term_mean) / 100 * areaa
        anomaly_in_time += anomaly_in_area
    anomalies.append(100*anomaly_in_time / total_area)


print('- Average of time series: '+str(numpy.average(anomalies)))
print('- Maximum of time series: '+str(numpy.max(anomalies)))
print('- Minimum of time series: '+str(numpy.min(anomalies)))
