"""
Keep-alive pinger for Render free tier services.
Pings the backend every 10 minutes to prevent spin-down.
"""
import requests
import time
from datetime import datetime

# Your Render ba