#!/usr/bin/python

# ZeroMQ PubSub Proxy (XSUB, XPUB)
# Maintains priority list. Dict of Array of varnames and list of sources, in order
# If data has not been received for 30 seconds, switch datasource if possible
# Periodically send priority list to Interfaces
# Receive messages with Source:Var key
# Send messages with Var# key, where # is one ASCII char giving position in priority list, ('0')=60=0, ('1')=61=1
# All the interface needs to know is that '0' is the default value, others are usually ignored
# Name of source can be determined by looking up in most recent priority list

# datasources.conf will define default highest priority sources
# If not defined, first come first server
# may be redefined at runtime with Priority message
# By default, Core will be highest priority unless explicitly defined as not