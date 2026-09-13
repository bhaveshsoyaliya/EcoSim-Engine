import math

def create_grid(lat, lon, size=5):
    """
    Create square grid around center.
    size = km
    """

    cells = []

    step = 0.00225      # ≈250 meters

    start_lat = lat - (size*0.009)/2
    start_lon = lon - (size*0.009)/2

    rows = int((size*0.009)/step)

    for r in range(rows):
        for c in range(rows):

            cell_lat = start_lat + r*step
            cell_lon = start_lon + c*step

            cells.append({
                "id": f"G{r}-{c}",
                "lat": cell_lat,
                "lon": cell_lon
            })

    return cells