#!/usr/bin/python

# When started, needs to be told location of Proxy
# An interface takes the datastreams ZeroMQ messages as input
# Always subscribe to the Priority list message
# Explicitly subscribe to variable names we want to receive
# Use REQ/REP sockets to communicate with Core, if it exists, any changes to settings or course layout.

# Interface types:
    # Web
    # Commandline
    # Logger

# Looks like Derby is best for web interface
# Meteor could be a runner up.
# Basically, we want python to end at handing off zeromq messages to a node.js powered web app
