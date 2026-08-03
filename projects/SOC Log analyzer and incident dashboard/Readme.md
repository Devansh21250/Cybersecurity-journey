SOC Log Analyzer & Dashboard

A lightweight SOC-style log analysis tool that detects brute-force attacks and generates a live HTML dashboard.

This analyzer consists of these features:
- Parse SSH auth logs for failed login attempts
- Detect brute-force attacks (threshold: >5 attempts per IP)
- Generate real-time HTML dashboard with alerts and charts
- Zero heavy dependencies — runs on any machine with Python

My understanding:
What we have done here is what SOC analyst do on a daily morning, checking if anyone has logged in or tried to log in via brute force, normally we do it via splunk but i have created this using python and it can be run on any machine. We read the log file to see if there is any failed password and note down their ip address and user, if it happens multiple times in the analyzer we mark it down as brute force attack. then we use flask to and html template to show such results on the dashboard.

How to Run
1. Install Flask: `pip install flask`
2. Run: `python app.py`
3. Open browser: `http://127.0.0.1:5000`
