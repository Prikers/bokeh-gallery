"""Plot all routes for a given airline on the world map

"""
import numpy as np
import pandas as pd
from pyproj import Geod

from bokeh.plotting import figure, save, output_file, reset_output
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout
from bokeh.tile_providers import WMTSTileSource
from bokeh.models.widgets import DataTable, TableColumn

from datasets import get_airports, get_routes, get_airlines

AIRLINE = 'Air France'

# =============================================================================
# Helper functions
# =============================================================================
def to_web_mercator(longitude, latitude):
    """Helper function to convert coordinates in Web Mercator projection. All 
    credits to Tom:
    http://www.neercartography.com/latitudelongitude-tofrom-web-mercator/
    
    """
    semimajorAxis = 6378137.0  # WGS84
    east = longitude * 0.017453292519943295
    north = latitude * 0.017453292519943295
    northing = 3189068.5 * np.log((1.0 + np.sin(north)) / (1.0 - np.sin(north)))
    easting = semimajorAxis * east 
    return easting, northing

def draw_route(lon_dep, lat_dep, lon_arr, lat_arr, nb_points=200):
    """Helper function to get evenly distributed points along a great circle 
    with a web mercator projection
    
    """
    gc = Geod(a=6378137.0, rf=298.257)
    lonlats = gc.npts(lon_dep, lat_dep, lon_arr, lat_arr, nb_points)
    longitudes = np.array([lon_dep] + [l[0] for l in lonlats] + [lon_arr])
    latitudes = np.array([lat_dep] + [l[1] for l in lonlats] + [lat_arr])
    return to_web_mercator(longitudes, latitudes)

# =============================================================================
# Main script
# =============================================================================
# 1. Prepare the data
# 1.1. Get datasets
all_routes  = get_routes()[['airlineID', 'airportID_dep', 'airportID_arr']]
all_airports = get_airports()
all_airlines = get_airlines()

# 1.2. Select airline
ID = all_airlines.loc[all_airlines.name == AIRLINE, 'airlineID'].values[0]

# 1.3. Filter airline's routes
routes = all_routes.loc[all_routes.airlineID == ID]
routes = (pd.merge(routes, all_airports, left_on='airportID_dep', right_on='airportID')
            .drop('airportID', axis=1))
routes = (pd.merge(routes, all_airports, left_on='airportID_arr', right_on='airportID',
                   suffixes=('_dep', '_arr'))
            .drop('airportID', axis=1))

# 1.4. Filter airline's visited airports
visited = (routes.IATA_dep.value_counts().rename('visits')
                 .reset_index().rename(columns={'index':'IATA'}))
airports = pd.merge(visited, all_airports, how='left', on='IATA')
airports['longitude'], airports['latitude'] = to_web_mercator(airports['longitude'], 
                                                              airports['latitude'])
airports['size'] = (3 + 10 * airports.visits / airports.visits.max()).round()

# 2. Draw the map
reset_output()
output_file('html/airline_routes.html')
url_map = 'https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png'
wikimap = WMTSTileSource(url=url_map)

west_bound, east_bound = to_web_mercator(-180, 180)
south_bound, north_bound = to_web_mercator(-66, 70)
fig = figure(plot_width=1060, plot_height=800,
             x_range=(west_bound, east_bound), 
             y_range=(south_bound, north_bound),
             tools='pan, wheel_zoom, save, help',
             title='All registered routes for {}'.format(AIRLINE))
fig.axis.visible = False
fig.add_tile(wikimap)

# 3. Plot the airports
source = ColumnDataSource(airports)
fig.circle(source=source, x='longitude', y='latitude', size='size')

# 4. Plot the routes
for i, row in routes.iterrows():
    if i % 100 ==0: print(i) # Takes some time to render all those routes!
    fig.line(*draw_route(row['longitude_dep'], row['latitude_dep'], 
                         row['longitude_arr'], row['latitude_arr']),
             alpha=0.2)

# 5. Table for top-visited airports
table = DataTable(source=source, width=500,
                  columns=[TableColumn(field='name', title='Airport'),
                           TableColumn(field='city', title='City', width=100),
                           TableColumn(field='visits', title='Count', width=100)])

save(layout([[fig, table]]))