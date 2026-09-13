import pandas as pd

TREE_DATABASE = [
    {
        "Species": "Neem",
        "Temp": (20, 45),
        "Rain": (400, 1200),
        "Soil": ["Alluvial", "Black", "Sandy"],
        "Carbon": 28,
        "Survival": 96
    },
    {
        "Species": "Peepal",
        "Temp": (18, 40),
        "Rain": (600, 1800),
        "Soil": ["Alluvial", "Clay"],
        "Carbon": 34,
        "Survival": 92
    },
    {
        "Species": "Banyan",
        "Temp": (20, 42),
        "Rain": (500, 1600),
        "Soil": ["Alluvial", "Black"],
        "Carbon": 41,
        "Survival": 90
    },
    {
        "Species": "Arjun",
        "Temp": (18, 38),
        "Rain": (700, 2000),
        "Soil": ["Clay", "Alluvial"],
        "Carbon": 36,
        "Survival": 94
    },
    {
        "Species": "Cassia",
        "Temp": (22, 42),
        "Rain": (500, 1500),
        "Soil": ["Sandy", "Black"],
        "Carbon": 24,
        "Survival": 91
    }
]


def recommend_species(temp, rainfall, soil):

    result = []

    for tree in TREE_DATABASE:

        score = 0

        if tree["Temp"][0] <= temp <= tree["Temp"][1]:
            score += 35

        if tree["Rain"][0] <= rainfall <= tree["Rain"][1]:
            score += 35

        if soil in tree["Soil"]:
            score += 30

        result.append({
            "Species": tree["Species"],
            "Suitability %": score,
            "Carbon Capture (kg/yr)": tree["Carbon"],
            "Survival %": tree["Survival"]
        })

    df = pd.DataFrame(result)

    return df.sort_values(
        "Suitability %",
        ascending=False
    )