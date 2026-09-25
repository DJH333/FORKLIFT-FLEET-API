from data_source import load_forklift_data
from fleet_analysis import fleet_health, analyze_fleet
from report import print_report, print_alerts

if __name__ == "__main__":
    forklifts = load_forklift_data()
    health_score = fleet_health(forklifts)
    summary = analyze_fleet(forklifts)
    print_report(forklifts, health_score, summary)
    print_alerts(summary["alerts"])
