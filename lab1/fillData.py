import redis
import pandas as pd
import time


def toString(arr):
    resStr = []
    for elem in arr:
        resStr.append(str(elem))

    return ' '.join(resStr)


def fillData(port, data):
    conn = redis.Redis(host='localhost', port=port)
    for row in data:
        key = row[0]
        value = toString(row[1:])
        conn.set(key, value)


st = time.time()

filename = 'data/svtl_meteo_20210604-20230304.csv'

df = pd.read_csv(filename, sep=',', header=0, names=['Datetime (UTC)', 'T (°C)', 'P (hPa)', 'Humidity (%)'])

length = len(df.values)
fillData(6380, df.values[0:length // 2])
fillData(6383, df.values[length // 2 + 1:])

et = time.time()

# get execution time in milliseconds
res = et - st
final_res = res
print('Databases were filled in ', final_res, 'seconds')
