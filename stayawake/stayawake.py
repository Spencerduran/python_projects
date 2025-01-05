"""
Mouse Movement Simulator for Work Hours

This script automatically moves the mouse cursor to random screen positions
during configured work hours to maintain an 'active' system status.
It checks the current time against defined work hours and lunch break,
moving the mouse only during valid work periods.

Configuration:
- Work hours: 8:00 AM - 5:00 PM
- Lunch break: 12:45 PM - 12:47 PM
- Movement interval: Every 550 seconds (approximately 9 minutes)
"""

import random as rnd
import time
from datetime import datetime
from datetime import time as dt_time

import pyautogui

# Calculate height and width of screen for setting movement boundaries
w, h = pyautogui.size()


def is_work_hours():
    """
    Check if current time is within defined work hours, excluding lunch break.

    Returns:
        bool: True if current time is during work hours and not lunch break
    """
    now = datetime.now().time()
    morning_start = dt_time(8, 00)  # 8:00 AM
    lunch_start = dt_time(12, 30)  # 12:45 PM
    lunch_end = dt_time(13, 30)  # 12:47 PM
    work_end = dt_time(17, 00)  # 5:00 PM

    # Check if current time is during lunch break
    if lunch_start <= now <= lunch_end:
        return False

    # Check if current time is during work hours (excluding lunch)
    return (morning_start <= now < lunch_start) or (lunch_end < now <= work_end)


# Main loop
while True:
    if is_work_hours():
        # Move mouse to a random location within screen boundaries
        pyautogui.move(rnd.randrange(0, w), rnd.randrange(0, h))
        now = datetime.now().time()
        print(f"tick {now}")
    else:
        now = datetime.now().time()
        print(f"Outside work hours or lunch break {now}")

    # Wait for next iteration (550 seconds ≈ 9 minutes)
    time.sleep(550)
