#!/bin/python
import mysql.connector as mariadb
import pandas as pd
import numpy as np
import copy

mydb = mariadb.connect( host="localhost", user="pigeon", passwd="root", database="haro" ) 

cursor = mydb.cursor(dictionary=True) 
query = '''
SELECT `entity`, `status`, `location`, `priority` FROM `notams`;
'''
cursor.execute(query)
sql_result = cursor.fetchall()
cursor.close()

df = pd.DataFrame(sql_result)
Xa = df.iloc[:, [0,1,3]]
Ya = df.iloc[:, [2]]


from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle

# lr = LogisticRegression()
# lr.fit(X_train, Y_train)

# print( ' Score : ' )
# print( lr.score[ X_test, Y_test ] )

enc = preprocessing.OneHotEncoder( handle_unknown='ignore' )
# print(Xa)
X = enc.fit_transform(Xa)
# print(X.columns)
model = LinearRegression(fit_intercept=False)
model.fit(X, Ya)

pickle.dump(model, open( 'lrm.sav', 'wb'))
pickle.dump(enc, open( 'enc.sav', 'wb'))


yb = np.array( [ 'CM', 'VOMM' ,'XX' ]).reshape(1, -1)
yt = enc.transform(yb)

# yt = enc.fit(yb.reshape(1,-1))
# print(Ya)
# print(new_model.predict(X))
# print( Ya.values )

cursor = mydb.cursor(dictionary=True) 
query = '''
SELECT `id`, `entity`, `status`, `location`, `priority` FROM `notams`;
'''
cursor.execute(query)
sql_result = cursor.fetchall()
cursor.close()
cursor = mydb.cursor(dictionary=True) 
query = '''
CALL e_smooth ( %s, %s, 0.3 )
'''
for notam in sql_result:
    nid = notam['id']
    ent = notam['entity']
    loc = notam['location']
    sta = notam['status']

    yb = np.array( [ ent, loc, sta ]).reshape(1, -1)
    yt = enc.transform(yb)
    val = model.predict(yt)[0][0] 

    print(val)
    cursor.execute( query, ( nid, float(val) ) )
cursor.close()
mydb.commit()
