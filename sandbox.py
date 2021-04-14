import fiona
import geopandas as gpd


data = gpd.read_file("resources/mastophaengt_armatur.gpkg")
data.head()  # P

# No need to pass "layer='etc'" if there's only one layer
with fiona.open('resources/mastophaengt_armatur.gpkg', layer='layer_of_interest') as layer:
    for feature in layer:
        print(feature['geometry'])