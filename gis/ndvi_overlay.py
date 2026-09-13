import os
import folium
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import reproject, Resampling
from pyproj import Transformer
from PIL import Image

def create_ndvi_overlay(ds):
    """
    Creates a clean, transparent georeferenced NDVI overlay map without rectangular background artifacts.
    """
    os.makedirs("temp", exist_ok=True)

    # 1. Read Sentinel Data
    red_data = ds.red.squeeze().values.astype(np.float32)
    nir_data = ds.nir.squeeze().values.astype(np.float32)

    # Valid data mask (sentinel invalid / zero values check)
    valid_mask = (red_data > 0) & (nir_data > 0) & (~np.isnan(red_data)) & (~np.isnan(nir_data))

    # Compute NDVI
    ndvi = np.zeros_like(red_data, dtype=np.float32)
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi[valid_mask] = (nir_data[valid_mask] - red_data[valid_mask]) / (nir_data[valid_mask] + red_data[valid_mask] + 1e-6)

    # 2. Extract UTM Bounds & CRS
    src_crs = str(ds.odc.crs) if hasattr(ds.odc, 'crs') else "EPSG:32643"
    
    west = float(ds.x.min())
    east = float(ds.x.max())
    south = float(ds.y.min())
    north = float(ds.y.max())

    height, width = ndvi.shape
    src_transform = from_bounds(west, south, east, north, width, height)

    # 3. Coordinate Transformation to Lat/Lon (WGS84)
    transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
    lon_min, lat_min = transformer.transform(west, south)
    lon_max, lat_max = transformer.transform(east, north)

    min_lat, max_lat = min(lat_min, lat_max), max(lat_min, lat_max)
    min_lon, max_lon = min(lon_min, lon_max), max(lon_min, lon_max)

    # 4. Reproject both NDVI array and Valid Mask
    dst_crs = "EPSG:4326"
    dst_transform = from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)
    
    dst_ndvi = np.zeros((height, width), dtype=np.float32)
    dst_mask = np.zeros((height, width), dtype=np.float32)

    reproject(
        source=ndvi,
        destination=dst_ndvi,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear
    )

    reproject(
        source=valid_mask.astype(np.float32),
        destination=dst_mask,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=Resampling.nearest
    )

    # 5. Build RGBA Image with True Alpha Mask
    norm = np.clip((dst_ndvi + 0.1) / 0.9, 0, 1)
    cmap = plt.get_cmap("RdYlGn")
    rgba = (cmap(norm) * 255).astype(np.uint8)

    # Make outside pixels & non-valid area completely transparent
    invalid = (dst_mask < 0.5) | (dst_ndvi == 0.0) | (np.isnan(dst_ndvi))
    rgba[invalid, 3] = 0  # Set Alpha to 0 (Invisible)

    img_path = "temp/ndvi_overlay.png"
    Image.fromarray(rgba, mode="RGBA").save(img_path)

    # 6. Setup Folium Map
    bounds = [[min_lat, min_lon], [max_lat, max_lon]]
    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )

    folium.raster_layers.ImageOverlay(
        image=img_path,
        bounds=bounds,
        opacity=0.6,
        interactive=True,
        name="Sentinel-2 NDVI Overlay"
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m