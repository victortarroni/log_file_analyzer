# Log File Analyzer

A lightweight Python CLI tool that parses Apache/Nginx-style access logs and produces a summary report of traffic volume, error rates, and top requesters — the kind of quick triage step an engineer reaches for when a server starts misbehaving and there's no time to read thousands of raw log lines by hand.

## Overview

Web servers and applications generate large volumes of log data continuously. When something goes wrong in production, engineers rarely have time to scroll through raw logs line by line — they need a fast summary: how many requests came in, what fraction failed, which IPs or endpoints are driving the load. This script automates that first-pass triage: it reads a combined-format access log, extracts structured fields via regex, aggregates the data, and prints a human-readable report covering total requests, bandwidth, HTTP error rate, and the top 5 IPs and paths by request volume.

## Key Features

- Parses standard Apache/Nginx "combined" log format lines into structured records (IP, timestamp, method, path, status, size)
- Streams the file line-by-line rather than loading it fully into memory, so it can handle large log files without excessive RAM use
- Silently skips malformed/non-matching lines instead of crashing
- Calculates total requests, total bytes transferred (converted to MB), and HTTP error rate (% of requests with status ≥ 400)
- Reports the top 5 most active IP addresses and top 5 most requested paths
- Includes a built-in mock-log generator so the script is runnable out of the box with no external log file required
- Wraps the full pipeline in centralized error handling (missing file vs. unexpected runtime errors)

## Architecture & Design Decisions

The script follows a simple three-layer pipeline, each function owning one responsibility:

```
main()
 ├─ parse_log_file()     # Input layer: file I/O + regex extraction + type normalization
 ├─ analyse_log_data()   # Logic layer: pure aggregation, no I/O or formatting
 └─ display_report()     # Presentation layer: formats and prints results
```

**Why this separation matters:** `analyse_log_data()` has no knowledge of files or terminal output — it just transforms a list of dicts into a metrics dict. That means it can be unit tested with in-memory fixtures, and it means swapping the output format later (JSON, CSV, an API payload) only touches `display_report()`, not the parsing or analysis logic.

**Streaming over `readlines()`:** the parser iterates the file object directly (`for line in file`) instead of loading the whole file into a list first. This keeps memory usage roughly constant regardless of log file size — a small but deliberate choice that matters once logs get into the gigabyte range.

**Guard clauses over nested conditionals:** both `parse_log_file()` (missing file) and `analyse_log_data()` (empty input) fail fast at the top of the function rather than letting a later line raise a less meaningful error (e.g. `ZeroDivisionError` on an empty list).

**Named regex groups:** the log pattern uses `(?P<ip>...)`, `(?P<status>...)`, etc. rather than positional groups, so `match.groupdict()` returns self-describing keys instead of a fragile tuple of indices.

## Tech Stack

All standard library — no third-party dependencies:

| Module | Why it was used |
|---|---|
| `re` | Purpose-built for pattern extraction from semi-structured text; the standard tool for slicing a raw log line into named fields without a full parser library. |
| `pathlib.Path` | Object-oriented, cross-platform path handling (`.exists()`, `.open()`) — cleaner and safer than raw string paths or `os.path`. |
| `typing` (`Dict`, `List`, `Any`) | Type hints as living documentation — makes function contracts explicit for IDEs, linters, and anyone reading the code without needing to guess at return shapes. |
| `collections.Counter` | Purpose-built frequency counter; simpler and more efficient than a manual dict-increment loop for the top-IP / top-path tallies. |

No external packages were needed for this scope — deliberately favoring the standard library keeps the script dependency-free and trivially portable.

## Setup & Usage

Requires Python 3.8+ (for f-string formatting and typing usage as written). No external dependencies to install.

```bash
git clone <your-repo-url>
cd <repo-folder>
python Main.py
```

On execution, the script generates a small mock `access.log` in the working directory, parses it, and prints the report to stdout. No arguments or configuration are required for this first run.

## Deployment

As currently written, the script is a **manually-run local CLI tool**: it hardcodes its target path to `access.log` in the working directory, and `main()` unconditionally regenerates that mock file on every run — which is fine for a demo, but means it isn't yet wired up to consume a real, externally-produced log file.

To move this toward an actually-deployed tool, the realistic path depends on how it'd be triggered:
- **Scheduled batch job** (cron / systemd timer / EventBridge + Lambda) if the goal is periodic triage of rotated logs — a natural fit since the tool already runs start-to-finish with no user interaction.
- **Event-driven** (Lambda triggered by a new log file landing in S3) if the goal is near-real-time analysis as logs are shipped — would require replacing the local file read with an S3 `get_object` call.

Either path requires removing the hardcoded mock-data generation and accepting the log source (file path or S3 key) as a parameter rather than a constant.

## Production Considerations

What I'd change before trusting this in a real environment:

- **Remove `generate_mock_logs()` from the execution path.** Right now `main()` overwrites `access.log` on every run — if a real log file with that name existed in the working directory, it would be silently destroyed. Mock data belongs in test fixtures, not the production code path.
- **Accept the log path as a CLI argument or event parameter** instead of the hardcoded `Path("access.log")` (note the unused `LOG_FILE_PATH` constant near the top of the file is dead code — `main()` defines its own path locally instead of using it).
- **Structured logging instead of `print()`** — JSON logs to stdout/CloudWatch so the tool's own output is machine-parseable, not just human-readable.
- **Narrow the broad `except Exception`** in `main()` — right now any unexpected error is swallowed into a generic message. In production this should log the full traceback (or re-raise after logging) rather than hide it.
- **Surface skipped/malformed lines** — the parser currently discards non-matching lines with no count or warning, which could quietly mask a log format change or data corruption.
- **Support additional log formats** (JSON logs, application-level INFO/WARN/ERROR logs) rather than only the Apache/Nginx combined format.
- **Unit tests** for `analyse_log_data()` in particular — it's pure logic with no I/O, so it's the easiest and highest-value function to cover.
- **CI/CD** — lint (flake8/ruff), type-check (mypy), and test on every push via GitHub Actions.
- **Metrics export**, if this were to run continuously — push the computed metrics (error rate, request volume) to CloudWatch or a similar system instead of only printing them, so trends can be tracked over time and alerted on.

## Limitations / Future Improvements

- Only parses the Apache/Nginx "combined" log format — other formats (JSON logs, custom application logs) aren't supported.
- Malformed lines are silently skipped with no count or log of how many were dropped.
- `generate_mock_logs()` runs unconditionally on every execution, overwriting `access.log` — this needs to be decoupled from `main()` before pointing the tool at a real log source.
- No CLI arguments — the log file path is hardcoded.
- No automated tests included yet.
- Error handling in `main()` currently uses a broad `except Exception`, which is fine for a learning project but would need to be more specific (and logged, not just printed) for production use.
