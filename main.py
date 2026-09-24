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


    for forklift in forklifts:

        forklift_id = forklift["forklift_id"]
        location = forklift["location"]
        battery = forklift["battery"]
        speed = forklift["speed"]
        status = forklift["status"]

        if location == "Charging Station":
            number_charging.append(forklift_id)
        if battery < 10:
            alerts.append(f"CRITICAL - {forklift_id} BATTERY: {battery}%")
        elif battery < 20:
            alerts.append(f"WARNING - {forklift_id} BATTERY: {battery}%")
        if speed > 6.0:
            alerts.append(f"{forklift_id} SPEED WARNING: {speed} mph")
        if status == "offline":
            alerts.append(f"{forklift_id} OFFLINE ALERT")
            number_offline.append(forklift_id)
        elif status == "active":
            number_active.append(forklift_id)

    return total_forklifts, number_active, number_charging, number_offline, alerts

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
        if forklift["speed"] > 6.0:
            health_score -= 5

    return max(health_score, 0)

def print_report(forklifts, health_score, total_forklifts, number_active, number_charging, number_offline, alerts):

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

Total Forklifts: {total_forklifts}
Active: {len(number_active)}
Charging: {len(number_charging)}
Offline: {len(number_offline)}
Alerts: {len(alerts)}""")

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
total_forklifts, number_active, number_charging,number_offline, alerts = analyze_fleet(forklifts)
print_report(forklifts, health_score, total_forklifts, number_active, number_charging,number_offline, alerts)
print_alerts(alerts)
