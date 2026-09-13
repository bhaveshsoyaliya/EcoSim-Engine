import math

def calculate_tree_requirement(grid_stats, pm25):

    output = []

    for g in grid_stats:

        veg = g["vegetation"]
        ndvi = g["ndvi"]

        # EcoSim Tree Deficit Index
        etdi = (
            (pm25 * 0.50)
            + ((1 - max(ndvi, 0)) * 35)
            + ((100 - veg) * 0.25)
        )

        trees = math.ceil(etdi * 1.8)

        if trees >= 150:
            priority = "Critical"
        elif trees >= 90:
            priority = "High"
        elif trees >= 40:
            priority = "Medium"
        else:
            priority = "Low"

        output.append({
            "Grid": f"G{g['row']}-{g['col']}",
            "NDVI": round(ndvi, 3),
            "Vegetation %": veg,
            "ETDI": round(etdi, 1),
            "Trees Needed": trees,
            "Priority": priority,
            "row": g["row"],
            "col": g["col"]
        })

    return output