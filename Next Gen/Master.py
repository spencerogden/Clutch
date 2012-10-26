#!/usr/bin/python



# Use subprocess to start various modules
# Keep track of PIDs to terminate when program is quit
# Receive messages from Interfaces to add or remove modules
# Manage Windows system tray
# Starts Proxy always
# master.conf Details initial modules setup (location, port)
# Starts each module, tells it where the Proxy is

# All components should periodically broadcast their location and status