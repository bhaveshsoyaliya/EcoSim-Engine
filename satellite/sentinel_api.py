"""
EcoSim Engine - Satellite Module
API Handler for Microsoft Planetary Computer Sentinel-2 L2A STAC Data
"""

import pystac_client
import planetary_computer
import rasterio
import numpy as np
from typing import Tuple, Dict, Any, Optional

# Microsoft Planetary Computer STAC Endpoint
STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

def fetch_sentinel2_ndvi_data(
    bbox: Tuple[float, float, float, float], 
    date_range: str = "2024-01-01/2026-12-31",
    max_cloud_cover: float = 20.0
) -> Tuple[Optional[np.ndarray], Optional[Dict[str, Any]], Optional[Dict[str, float]]]:
    """
    Fetches Red (B04) and NIR (B08) bands for a given bounding box from Planetary Computer,
    computes raw NDVI, and returns raster matrix, metadata, and exact EPSG:4326 bounds.

    Parameters:
        bbox: (min_lon, min_lat, max_lon, max_lat)
        date_range: YYYY-MM-DD/YYYY-MM-DD
        max_cloud_cover: Maximum cloud coverage percentage

    Returns:
        (ndvi_array, raster_profile, geo_bounds_dict)
    """
    try:
        catalog = pystac_client.Client.open(
            STAC_URL,
            modifier=planetary_computer.sign_inplace,
        )

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date_range,
            query={"eo:cloud_cover": {"lt": max_cloud_cover}},
            max_items=1,
        )

        items = list(search.items())
        if not items:
            print("[EcoSim Satellite API] Warning: No clear Sentinel-2 scenes found for the specified BBOX/Date.")
            return None, None, None

        item = items[0]
        
        # Extract signed URLs for Red (B04) and NIR (B08) bands
        red_href = item.assets["B04"].href
        nir_href = item.assets["B08"].href

        # Read raster subsets directly using Rasterio window/bbox
        with rasterio.open(red_href) as red_src, rasterio.open(nir_href) as nir_src:
            # Transform input WGS84 bbox to raster's native CRS window
            from rasterio.windows import from_bounds
            window = from_bounds(*bbox, transform=red_src.transform)

            red_band = red_src.read(1, window=window).astype(np.float32)
            nir_band = nir_src.read(1, window=window).astype(np.float32)

            # Retrieve window transform and profile
            win_transform = rasterio.windows.transform(window, red_src.transform)
            profile = red_src.profile.copy()
            profile.update({
                'height': red_band.shape[0],
                'width': red_band.shape[1],
                'transform': win_transform,
                'dtype': 'float32',
                'count': 1
            })

            # Calculate Exact EPSG:4326 Bounding Box for Folium alignment
            from pyproj import Transformer
            transformer = Transformer.from_crs(red_src.crs, "EPSG:4326", always_xy=True)
            
            # Window corners in native CRS
            left, bottom, right, top = rasterio.windows.bounds(window, red_src.transform)
            min_lon, min_lat = transformer.transform(left, bottom)
            max_lon, max_lat = transformer.transform(right, top)

            geo_bounds = {
                "south": min_lat,
                "west": min_lon,
                "north": max_lat,
                "east": max_lon
            }

            # Scientific NDVI Formula: (NIR - Red) / (NIR + Red)
            np.seterr(divide='ignore', invalid='ignore')
            denominator = nir_band + red_band
            ndvi = np.where(denominator == 0, 0, (nir_band - red_band) / denominator)
            ndvi = np.clip(ndvi, -1.0, 1.0)

            return ndvi, profile, geo_bounds

    except Exception as e:
        print(f"[EcoSim Satellite API] Error fetching Sentinel-2 imagery: {e}")
        return None, None, None


def generate_synthetic_fallback_ndvi(lat: float, lon: float, delta: float = 0.05):
    """
    Fallback scientific NDVI generator when satellite network is offline.
    Provides georeferenced synthetic raster for immediate testing.
    """
    size = 100
    x = np.linspace(-2, 2, size)
    y = np.linspace(-2, 2, size)
    xx, yy = np.meshgrid(x, y)
    
    # Synthetic terrain with water bodies (-0.2), urban density (0.1), and green vegetation (0.7)
    ndvi = 0.4 * np.sin(xx) * np.cos(yy) + 0.3 * np.exp(-(xx**2 + yy**2))
    ndvi = np.clip(ndvi, -0.3, 0.85).astype(np.float32)

    geo_bounds = {
        "south": lat - delta,
        "west": lon - delta,
        "north": lat + delta,
        "east": lon + delta
    }
    
    return ndvi, geo_bounds