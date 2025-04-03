import random as rnd
import time
from datetime import datetime
from datetime import time as dt_time

import pyautogui

# Calculate height and width of screen for setting movement boundaries
w, h = pyautogui.size()

# Define the central area (500x500 pixels) of the screen
center_x = w // 2
center_y = h // 2
area_size = 500  # 500x500 pixel area
x_min = center_x - (area_size // 2)
x_max = center_x + (area_size // 2)
y_min = center_y - (area_size // 2)
y_max = center_y + (area_size // 2)


def is_work_hours():
    """
    Check if current time is within defined work hours, excluding lunch break.
    Returns:
        bool: True if current time is during work hours and not lunch break
    """
    now = datetime.now().time()
    morning_start = dt_time(8, 00)  # 8:00 AM
    lunch_start = dt_time(12, 30)  # 12:30 PM
    lunch_end = dt_time(13, 30)  # 1:30 PM
    work_end = dt_time(20, 00)  # 8:00 PM

    # Check if current time is during lunch break
    if lunch_start <= now <= lunch_end:
        return False

    # Check if current time is during work hours (excluding lunch)
    return (morning_start <= now < lunch_start) or (lunch_end < now <= work_end)


# Main loop
while True:
    if is_work_hours():
        # Get current position
        current_x, current_y = pyautogui.position()

        # Generate small relative movement (between -100 and 100 pixels)
        move_x = rnd.randrange(-100, 101)
        move_y = rnd.randrange(-100, 101)

        # Calculate new position
        new_x = current_x + move_x
        new_y = current_y + move_y

        # Constrain to stay within boundaries
        new_x = max(x_min, min(x_max, new_x))
        new_y = max(y_min, min(y_max, new_y))

        # Move mouse to the constrained position
        pyautogui.moveTo(new_x, new_y)

        now = datetime.now().time()
        print(f"Moved mouse by ({move_x}, {move_y}) to ({new_x}, {new_y}) at {now}")
    else:
        now = datetime.now().time()
        print(f"Outside work hours or lunch break {now}")

    # Wait for next iteration (550 seconds ≈ 9 minutes)
    time.sleep(550)
