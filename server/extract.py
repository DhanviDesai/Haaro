import requests
import pandas
import json
api_key='8ea8c220-3859-11e9-9265-5985bd35eb75'
df = pandas.read_csv('airspace.csv')
details=[]
for i in range(len(df)):
    d={}
    now = df.iloc[i]
    fir =now.values[0]
    name=now.values[1] 
    print(fir)
    req_url = 'https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/airspaces/zones/fir-list?format=json&api_key=8ea8c220-3859-11e9-9265-5985bd35eb75&firs={0}'.format('VOMF')
    resp=requests.get(req_url)
    jsons = json.loads(resp.text)
    op = {}
    op["properties"] = jsons[0]['properties']
    op['properties']['name'] = name
    op['coordinates'] = jsons[0]['coordinates'] 
    details.append(op)
df2=pandas.DataFrame(details)
df2.to_json("./airports_coordinates.json")