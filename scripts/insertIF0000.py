import pandas as pd
import numpy as np
import os 
import pymongo

os.chdir('D:/Programms/vnpy/examples/CtaBacktesting')

data = pd.read_csv('IF0000_1min.csv')

data.Date = [int(x.replace('-','')) for x in data.Date]
data=data[data.Date>=20100421]

#Insert into mongo
client = pymongo.MongoClient('localhost',27017)
db = client.Jax_1Min_Db
collection = db.IF0000
count = 0
for index,line in data.iterrows():
    new_post = dict(line)
    collection.insert_one(new_post)
    count = count + 1
    if count %20 == 0:
        print('finish inserting %s'%count)

client.close()