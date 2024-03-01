import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon

# Coordinates provided by the user
coordinates = [
    [-62.75225, 45.47434],
    [-62.75712, 45.47581],
    [-62.77153, 45.49617],
    [-62.74912, 45.50576],
    [-62.7464, 45.486],
    [-62.75225, 45.47434]  # Closing the polygon by repeating the first point
]

# Create a Polygon
polygon = Polygon(coordinates)

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(index=[0], crs='EPSG:4326', geometry=[polygon])

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
gdf.boundary.plot(ax=ax)
plt.show()
import contextily as ctx

# Convert the coordinates to Web Mercator for contextily compatibility
gdf_wm = gdf.to_crs(epsg=3857)

# Plotting on a map
fig, ax = plt.subplots(figsize=(10, 10))
gdf_wm.plot(ax=ax, alpha=0.5, edgecolor='black', color='blue')
ctx.add_basemap(ax, source=ctx.providers.Stamen.Terrain)

# Adjusting the view to the data
ax.set_axis_off()
plt.tight_layout()
plt.show()
