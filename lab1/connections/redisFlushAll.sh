#!/bin/bash

echo FLUSHALL | redis-cli -p 6380
echo FLUSHALL | redis-cli -p 6383
