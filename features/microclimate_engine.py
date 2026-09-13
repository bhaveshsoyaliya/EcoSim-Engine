import numpy as np
import pandas as pd


def simulate_microclimate(
    temperature,
    humidity,
    wind_speed,
    vegetation_percent,
    builtup_percent,
    water_percent,
    grid_size=20,
):
    """
    EcoSim Micro-Climate Engine
    Returns urban heat island simulation results.
    """

    np.random.seed(42)

    cells = []

    for r in range(grid_size):
        for c in range(grid_size):

            veg = np.clip(
                vegetation_percent + np.random.normal(0, 12),
                0, 100
            )

            built = np.clip(
                builtup_percent + np.random.normal(0, 10),
                0, 100
            )

            water = np.clip(
                water_percent + np.random.normal(0, 5),
                0, 100
            )

            surface_temp = (
                temperature
                + built * 0.05
                - veg * 0.04
                - water * 0.03
                - wind_speed * 0.12
                + np.random.normal(0, 0.5)
            )

            local_humidity = np.clip(
                humidity + veg * 0.08 - built * 0.05,
                20, 100
            )

            heat_index = surface_temp + (100 - local_humidity) * 0.02

            cooling = veg * 0.35 + water * 0.45

            if heat_index >= 38:
                priority = "Critical"
            elif heat_index >= 34:
                priority = "High"
            elif heat_index >= 30:
                priority = "Moderate"
            else:
                priority = "Low"

            cells.append({
                "Grid": f"G{r}-{c}",
                "Row": r,
                "Col": c,
                "Vegetation %": round(veg, 1),
                "Built-up %": round(built, 1),
                "Water %": round(water, 1),
                "Surface Temp": round(surface_temp, 1),
                "Humidity": round(local_humidity, 1),
                "Heat Index": round(heat_index, 1),
                "Cooling Score": round(cooling, 1),
                "Priority": priority,
            })

    df = pd.DataFrame(cells)

    return {
        "avg_temp": round(df["Surface Temp"].mean(), 2),
        "heat_island": round(df["Heat Index"].mean(), 2),
        "cooling": round(df["Cooling Score"].mean(), 2),
        "critical_cells": int((df["Priority"] == "Critical").sum()),
        "grid": df,
    }