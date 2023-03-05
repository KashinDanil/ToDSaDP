#!/bin/bash

echo replicaof localhost 6380 | redis-cli -p 6381
echo replicaof localhost 6380 | redis-cli -p 6382
echo replicaof localhost 6383 | redis-cli -p 6384
echo replicaof localhost 6383 | redis-cli -p 6385
