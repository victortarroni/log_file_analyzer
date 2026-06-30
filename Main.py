import re
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


#region - Regular expression blueprint

# Regular expression blueprint for a standard Apache/Nginx combined log format
# Example line: 127.0.0.1 - - [27/Jun/2026:12:01:02 +0000] "GET /index.html HTTP/1.1" 200 1043

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\d+|-)'
)

#endregion

#this is where we will decide the file path
LOG_FILE_PATH = Path("logs/access.log")

#region

def parse_log_file(file_path: Path) -> List[Dict[str, Any]]:
    parsed_logs = []
    
    if not file_path.exists():
        raise FileNotFoundError(f"Target log file not found at: {file_path}")
        
    with file_path.open("r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            match = LOG_PATTERN.match(line.strip())
            if not match:
                # Proactive edge-case handling: skip malformed lines
                continue
                
            entry = match.groupdict()
            # Cast numerical fields early to avoid downstream string operations
            entry["status"] = int(entry["status"])
            entry["size"] = 0 if entry["size"] == "-" else int(entry["size"])
            parsed_logs.append(entry)
            
    return parsed_logs

#endregion

#region - analyse_log_data function

#Now that we have parsed our logs into a clean list of dictionaries, we need a module to compute the statistics: top requested endpoints, total bandwidth, and error rates.

def analyse_log_data(parsed_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not parsed_logs:
        return {"total_requests": 0, "top_ips": [], "top_paths": [], "error_rate": 0.0, "total_bytes": 0}

    total_requests = len(parsed_logs)
    total_bytes = sum(entry["size"] for entry in parsed_logs)
    
    ip_counter = Counter(entry["ip"] for entry in parsed_logs)
    path_counter = Counter(entry["path"] for entry in parsed_logs)
    
    # Calculate error rate (status codes >= 400 indicate client/server errors)
    error_count = sum(1 for entry in parsed_logs if entry["status"] >= 400)
    error_rate = (error_count / total_requests) * 100

    return {
        "total_requests": total_requests,
        "total_bytes": total_bytes,
        "top_ips": ip_counter.most_common(5),
        "top_paths": path_counter.most_common(5),
        "error_rate": round(error_rate, 2)
    }
#endregion

#region - display_report

#What it does: This function takes the final dictionary of aggregated metrics and prints a structured, human-readable summary report to the terminal, including data volume conversions and top-five distributions.

#Why it exists architecturally: This represents the presentation layer of the application. By separating output formatting into its own module, you ensure that transitioning the tool in the future—such as generating an HTML report, sending a JSON payload to an API, or writing to a CSV file—requires changing only this presentation function, leaving your core analytical and parsing engines completely untouched.

def display_report(metrics: Dict[str, Any]) -> None:
    if metrics["total_requests"] == 0:
        print("=== Log Analysis Report ===")
        print("No valid log entries found to analyze.")
        return

    print("=== Log Analysis Report ===")
    print(f"Total Requests Processed : {metrics['total_requests']}\n")
    
    # Format bytes to a human-readable Megabyte format
    mb_transferred = metrics["total_bytes"] / (1024 * 1024)
    print(f"Total Data Transferred   : {mb_transferred:.2f} MB")
    print(f"HTTP Error Rate          : {metrics['error_rate']}%\n")
    
    print("Top 5 Most Active IP Addresses:")
    for ip, count in metrics["top_ips"]:
        print(f"  - {ip}: {count} requests")
        
    print("\nTop 5 Most Requested Paths:")
    for path, count in metrics["top_paths"]:
        print(f"  - {path}: {count} requests")
    print("=" * 27)

#endregion