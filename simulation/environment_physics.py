import numpy as np

def simulate_pm25(current_pm25, temperature, wind, rain):

    values = []

    pm = current_pm25

    for hour in range(24):

        # Temperature increases pollution slightly
        temp_effect = (temperature - 20) * 0.12

        # Wind removes pollution
        wind_effect = wind * 0.35

        # Rain washes particles
        rain_effect = rain * 2.0

        # Natural fluctuation
        fluctuation = np.sin(hour/2.5) * 3

        pm = pm + temp_effect - wind_effect - rain_effect + fluctuation

        pm = max(pm,0)

        values.append(round(pm,1))

    return values