import pandas as pd
from simulation.environment_physics import simulate_pm25

def forecast_pm25(pm25, temperature, wind, rain):

    values = simulate_pm25(
        pm25,
        temperature,
        wind,
        rain
    )

    return pd.DataFrame({
        "Hour": list(range(24)),
        "PM 2.5": values
    })