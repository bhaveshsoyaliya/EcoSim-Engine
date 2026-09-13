def calculate_wqi(ph, bod, cod, do):

    score = 100

    # pH
    if ph < 6.5 or ph > 8.5:
        score -= 20

    # BOD
    if bod > 3:
        score -= (bod - 3) * 5

    # COD
    if cod > 25:
        score -= (cod - 25) * 1

    # Dissolved Oxygen
    if do < 6:
        score -= (6 - do) * 8

    score = max(0, min(100, score))

    if score >= 90:
        quality = "Excellent"

    elif score >= 70:
        quality = "Good"

    elif score >= 50:
        quality = "Moderate"

    else:
        quality = "Polluted"

    return round(score,1), quality