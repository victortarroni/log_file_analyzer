# Log File Analyzer

## Overview

The **Log File Analyzer** is a Python project that reads application log files and generates a concise summary of their contents.

System administrators, Cloud Engineers, and DevOps Engineers work with log files every day to diagnose problems, monitor applications, and investigate incidents. This project simulates a real-world log analysis tool by automatically identifying log levels and reporting useful statistics.

Rather than manually reading thousands of log entries, the script produces a clear summary within seconds.

---

## Features

* Read log files from disk
* Count the number of:

  * **INFO** messages
  * **WARNING** messages
  * **ERROR** messages
* Identify the most common error message
* Handle invalid or missing files gracefully
* Modular architecture designed for future expansion

---

## Example Log File

```text
INFO User logged in
ERROR Database connection failed
WARNING CPU usage high
ERROR S3 bucket inaccessible
INFO Backup completed
```

## Example Output

```text
Errors: 2
Warnings: 1
Info: 2

Most common error:
Database connection failed
```

---

## Technologies Used

* Python 3
* File Handling
* Regular Expressions (Regex)
* Dictionaries
* Exception Handling
* Modular Programming

---

## Project Structure

The project follows a production-style modular architecture.

Instead of placing all functionality inside a single Python file, responsibilities are separated into independent modules. This makes the code easier to maintain, test, and extend.

The project is designed around three main responsibilities:

* Parsing log files
* Analysing log data
* Reporting the results

This separation of concerns reflects how production software is commonly organised.

---

## Why I Built This Project

I built this project to strengthen the Python skills required for Cloud Engineering roles.

Cloud Engineers spend a significant amount of time analysing logs from applications, virtual machines, containers, Kubernetes clusters, and cloud services. Automating log analysis is therefore a practical and valuable skill.

This project demonstrates the ability to:

* Process real-world text files
* Extract structured information from unstructured data
* Design maintainable Python applications
* Build software using modular architecture
* Apply clean coding practices

---

## Future Improvements

Planned enhancements include:

* Export reports to CSV
* Search logs by date or time
* Add coloured terminal output
* Process multiple log files simultaneously
* Generate summary reports
* Support additional log formats

---

## Learning Objectives

This project was created to practise:

* File handling
* Regular expressions
* Dictionaries
* Error handling
* Software architecture
* Clean code principles
* Modular design

---

## Documentation

The goal of this project is to teach a computer how to analyse large log files automatically.

Every application keeps a log file that records important events such as successful operations, warnings, and errors. These files can quickly grow to thousands of lines, making manual analysis slow and inefficient.

The Log File Analyzer acts like an automated assistant, reading the log file and producing a concise summary that highlights the most important information. This approach reflects a common task performed by Cloud Engineers and Site Reliability Engineers (SREs) when troubleshooting systems.

---

## Author

Victor Tarroni

Aspiring Cloud Engineer | Python | Automation | Google Cloud Platform
