To start run `./ETL.sh`.
It starts all redis connections (All configs must be ready in advance on ports 6380-6385)
Then makes replicas of two main servers (6380 to 6381, 6382 and 6383 to 6384, 6385)
Then reads file from data/svtl_meteo_20210604-20230304.csv and 
evenly distributes the data between two servers (6380, 6383)
And finally, begins listening the queue to collect data from different redis servers and providing it to client

Meanwhile, you run `python client.py` to start asking data
