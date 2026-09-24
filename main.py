import json
from datetime import datetime

def load_forklift_data():
    with open("forklift_data.json", "r") as file:
        forklifts = (json.load(file))
    return forklifts



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

def print_report(forklifts, health_score, summary):

    print(f"""
--------------------
FORKLIFT REPORT
--------------------""")

    print(f"""
GENERATED: {datetime.today()}""")

    print(f"""
FLEET HEALTH: {health_score}%""")

    print(f"""
------------------
FLEET SUMMARY
------------------

Total Forklifts: {summary["total_forklifts"]}
Active: {len(summary["active"])}
Charging: {len(summary["charging"])}
Offline: {len(summary["offline"])}
Maintenance: {len(summary["maintenance"])}
Alerts: {len(summary["alerts"])}""")

    print(f"""
--------------------
INDIVIDUAL REPORTS: 
--------------------""")

    for forklift in forklifts:

        print(f"""
ID: {forklift["forklift_id"]}   
Location: {forklift["location"]}
Battery: {forklift["battery"]}%
Speed: {forklift["speed"]}
Status: {forklift["status"]}""")

def print_alerts(alerts):

    if alerts:
        print(f"""
------------------    
    ALERTS:
------------------""")
        for alert in alerts:
            print(f"""    {alert}""")
    else:
        print(f"""
------------------    
    NO ALERTS:
------------------""")

forklifts = load_forklift_data()
health_score = fleet_health(forklifts)
summary = analyze_fleet(forklifts)
print_report(forklifts, health_score, summary)
print_alerts(summary["alerts"])
