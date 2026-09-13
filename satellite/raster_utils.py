import numpy as np

def classify_ndvi(ndvi):
    """Convert NDVI into vegetation percentage."""

    green = np.where(ndvi > 0.35, 1, 0)

    return green

def grid_statistics(ndvi, rows=20, cols=20):

    h, w = ndvi.shape

    cell_h = h // rows
    cell_w = w // cols

    results = []

    for r in range(rows):
        for c in range(cols):

            y1 = r * cell_h
            y2 = (r + 1) * cell_h

            x1 = c * cell_w
            x2 = (c + 1) * cell_w

            cell = ndvi[y1:y2, x1:x2]

            avg = float(np.nanmean(cell))

            vegetation = float((cell > 0.35).mean() * 100)

            results.append({
                "row": r,
                "col": c,
                "ndvi": round(avg, 3),
                "vegetation": round(vegetation, 1)
            })

    return results