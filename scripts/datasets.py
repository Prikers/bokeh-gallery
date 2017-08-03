import pandas as pd

def get_airports():
    url = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat'
    cols = ['airportID', 'name', 'city', 'country', 'IATA', 'ICAO', 'latitude', 
            'longitude', 'altitude']
    airports = pd.read_csv(url, header=None, usecols=list(range(9)), names=cols)
    return airports

def get_routes():
    url = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat'
    cols = ['airline', 'airlineID', 'airport_dep', 'airportID_dep',
            'airport_arr', 'airportID_arr']
    routes = pd.read_csv(url, header=None, usecols=list(range(6)), names=cols,
                         na_values='\\N').dropna()
    return routes

def get_airlines():
    url = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat'
    cols = ['airlineID', 'name', 'IATA', 'ICAO']
    airlines = pd.read_csv(url, header=None, usecols=[0, 1, 3, 4], names=cols)
    return airlines