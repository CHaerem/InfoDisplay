from mpl_toolkits.basemap import Basemap

m = Basemap(projection='mill', lat_0=50, lon_0=-100, resolution='l', area_thresh=10000)
print("Reading shapefile...")
m.readshapefile(f'/Users/cher/Documents/Globe/shapefiles/World_Countries/World_Countries', 'countries', drawbounds=True, linewidth=1, color='black')
print("Shapefile read.")

#exec(open('LoadShapes.py').read())