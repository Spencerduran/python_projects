from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from AppKit import NSWorkspace
import subprocess

window_title = "Windows 11 (1)"


def find_window(window_title):
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for window in window_list:
        if window.get('kCGWindowName') == window_title:
            return window
    return None


def switch_to_window(window_pid):
    try:
        workspace = NSWorkspace.sharedWorkspace()
        app = workspace.runningApplications()
        for running_app in app:
            if running_app.processIdentifier() == window_pid:
                workspace.launchApplication_(running_app.localizedName())
                break
    except Exception as e:
        print(f"Error switching to the window: {e}")


if __name__ == "__main__":
    window = find_window(window_title)
    if window:
        window_pid = window.get('kCGWindowOwnerPID')
        switch_to_window(window_pid)
    else:
        print(f"No window found with the title '{window_title}'")
