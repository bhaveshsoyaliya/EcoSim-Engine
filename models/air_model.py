def calculate_aqi(pm25, pm10):
    # Handle missing API values
    pm25 = 0 if pm25 is None else float(pm25)
    pm10 = 0 if pm10 is None else float(pm10)

    if pm25 <= 15:
        return "GOOD", "green"

    elif pm25 <= 35:
        return "MODERATE", "orange"

    elif pm25 <= 55:
        return "UNHEALTHY FOR SENSITIVE", "darkorange"

    elif pm25 <= 100:
        return "UNHEALTHY", "red"

    else:
        return "HAZARDOUS", "darkred"