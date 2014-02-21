#!/usr/bin/python

# Core needs location of Proxy
# Will start its own Filemonitor thread
# May start a pool of function calc worker threads
# Master keeper of last known value of each variable
# Maintain list of functions and the vars they depend on. 
# When a message comes in, calc all functions which depend on it and send results
# Subscribe to various control messages such as Clock, Mark, Table, etc
# Write any table or function changes back to files
# Send results of function calculation to Proxy
# Core is just another data provider, it may not be the highest priority provider for a variable


# Should functions be stored as ConfObj files? Could make reloading easier


# test
