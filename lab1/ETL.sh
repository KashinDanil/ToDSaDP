#!/bin/bash

# Start Redis connections
connections/redisStart.sh

# Make replicas
connections/redisMakeReplicas.sh

# Fill Redis with data
python fillData.py

# Run server
python server.py

# Flush all data
#connections/redisFlushAll.sh

# Stop Redis connections
#connections/redisStop.sh
