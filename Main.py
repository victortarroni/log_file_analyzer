import re
from pathlib import Path
from typing import Dict, List, Any


#region - Regular expression blueprint

# Regular expression blueprint for a standard Apache/Nginx combined log format
# Example line: 127.0.0.1 - - [27/Jun/2026:12:01:02 +0000] "GET /index.html HTTP/1.1" 200 1043

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) (?P<size>\d+|-)'
)

#endregion

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