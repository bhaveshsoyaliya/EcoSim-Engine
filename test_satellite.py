from satellite.cdse_api import download_sentinel
from satellite.ndvi import calculate_ndvi, green_cover

import matplotlib.pyplot as plt

LAT = 23.0225
LON = 72.5714

print("Searching latest Sentinel image...")

ds = download_sentinel(LAT, LON)

if ds is None:
    raise Exception("No Sentinel image found")

ndvi = calculate_ndvi(ds)

print("Green Cover:", green_cover(ndvi), "%")

plt.figure(figsize=(8,8))
plt.imshow(ndvi, cmap="RdYlGn")
plt.colorbar(label="NDVI")
plt.title("Real NDVI - Ahmedabad")
plt.axis("off")
plt.show()