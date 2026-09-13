from pystac_client import Client
from odc.stac import load
import pandas as pd

CATALOG = "https://earth-search.aws.element84.com/v1"

def download_sentinel(lat, lon, radius=0.025):

    catalog = Client.open(CATALOG)

    bbox = (
        lon - radius,
        lat - radius,
        lon + radius,
        lat + radius
    )

    # Last 180 days
    end = pd.Timestamp.utcnow().date()
    start = end - pd.Timedelta(days=180)

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": 40}}
    )

    items = list(search.items())

    if len(items) == 0:
        return None

    # Lowest cloud image first
    items = sorted(
        items,
        key=lambda i: i.properties.get("eo:cloud_cover", 100)
    )

    ds = load(
        items[:1],
        bands=["red", "nir"],
        bbox=bbox,
        resolution=10,
        chunks={}
    )

    return {
    "dataset": ds,
    "bbox": bbox
}