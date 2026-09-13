def calculate_carbon(vehicles, industries, trees, solar):

    # Daily CO₂ emission (kg/day)
    vehicle_emission = vehicles * 4.6
    industry_emission = industries * 120

    total_emission = vehicle_emission + industry_emission

    # Carbon absorption
    tree_absorption = trees * 0.06
    solar_reduction = solar * 0.8

    absorbed = tree_absorption + solar_reduction

    net = total_emission - absorbed

    score = max(0, min(100, 100 - (net / 20)))

    return {
        "total": round(total_emission,1),
        "absorbed": round(absorbed,1),
        "net": round(net,1),
        "score": round(score,1)
    }