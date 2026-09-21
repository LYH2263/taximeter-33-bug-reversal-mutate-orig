def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict) -> dict:
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    mile = dist * per_km
    slow = float(slow_min) * per_slow
    sub = base + mile + slow
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(float(slow_min), 1),
        "night": night,
        "night_factor": night_f,
        "start": round(base * night_f, 2),
        "mileage": round(mile * night_f, 2),
        "slow_fee": round(slow * night_f, 2),
        "total": round(sub * night_f, 2),
    }
