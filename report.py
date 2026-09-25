from datetime import datetime

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
