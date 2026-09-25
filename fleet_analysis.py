def analyze_fleet(forklifts):

    alerts = []
    total_forklifts = len(forklifts)
    number_active = []
    number_charging = []
    number_offline = []
    number_maintenance = []


    for forklift in forklifts:

        forklift_id = forklift["forklift_id"]
        battery = forklift["battery"]
        speed = forklift["speed"]
        status = forklift["status"]

        if status == "offline":
            alerts.append(f"{forklift_id} OFFLINE ALERT")
            number_offline.append(forklift_id)
        elif status == "active":
            number_active.append(forklift_id)
        elif status == "charging":
            number_charging.append(forklift_id)
        elif status == "maintenance":
            number_maintenance.append(forklift_id)
            alerts.append(f"{forklift_id} UNDER MAINTENANCE")
        else:
            alerts.append(f"{forklift_id} UNKNOWN STATUS: '{status}'")
        if battery < 10:
            alerts.append(f"CRITICAL - {forklift_id} BATTERY: {battery}%")
        elif battery < 20:
            alerts.append(f"WARNING - {forklift_id} BATTERY: {battery}%")
        if speed > 6.0:
            alerts.append(f"{forklift_id} SPEED WARNING: {speed} mph")

    return {
        "total_forklifts": total_forklifts,
        "active": number_active,
        "charging": number_charging,
        "offline": number_offline,
        "maintenance": number_maintenance,
        "alerts": alerts,
    }

def fleet_health(forklifts):

    health_score = 100

    for forklift in forklifts:
        forklift_id = forklift["forklift_id"]
        location = forklift["location"]
        battery = forklift["battery"]
        speed = forklift["speed"]
        status = forklift["status"]

        if forklift["battery"] < 20:
            health_score -= 10
        if forklift["status"] == "offline":
            health_score -= 10
        if forklift["status"] == "maintenance":
            health_score -= 5
        if forklift["speed"] > 6.0:
            health_score -= 5

    return max(health_score, 0)
