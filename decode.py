import requests
from bs4 import BeautifulSoup
import json
import sys
from flask import Flask, jsonify, request
from pymongo import MongoClient

client = MongoClient()
db = client.harodb

app = Flask(__name__)

def find_insights(raw_notam):
    url = "http://www.drorpilot.com/cgi-bin/Notam.pl"
    postdata = { "enote": raw_notam }
    headers = { "Content-Type":"application/x-www-form-urlencoded" }
    response = requests.post(url,headers=headers,data=postdata)
    html = BeautifulSoup(response.text,features="html.parser")

    temp = ""

    for tabletag in html.find_all('table',{'id':'notamTable'}):
        for trtag in tabletag.find_all('tr'):
            for tdtag in trtag.find_all('td'):
                if not tdtag.has_attr('s'):
                    temp = temp+"\n\n"+tdtag.text

    r = temp.split("\n\n")
    r = [ x.strip() for x in r ]
    r = list(r)
    plaintext = r[10]

    custom_structure = { "FIR":r[2], "Scope":r[5], "Schedule":r[8], "Subject":r[12], "Limits":r[15], "From":r[18], "Status":r[21], "Position":r[24], "Traffic":r[30], "Radius":r[33], "To":r[36], "Purpose":r[39], "ICAO_Code":r[42] }
    custom_structure["Plaintext"] = plaintext

    return custom_structure

@app.route('/api/insights')
def extract_notams():
    query = request.args["query"]
    notam_decoded = find_insights(query)
    return notam_decoded

@app.route('/api/airports')
def extract_notams_from_airport():
    code = request.args["location"]
    sub = request.args["sub"]
    print("=========")
    print("=========")

    # Check if code exists in cache
    code_list = list(db.cache_icao.find({'code': code}))
    current_code_data = None

    data = []

    if len(code_list) == 0:
        print("Code is new. Querying for the first time...")

        requrl = "https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/states/notams/notams-list?format=json&api_key=9d849040-30e7-11e9-9872-b90b55b59c3d&locations="+code
        response = requests.get(requrl).json()

        obj = {
            "code": code,
            "response": response
        }

        db.cache_icao.insert_one(obj)
        current_code_data = obj

    else:
        print("Code found in cache. Setting from the DB...")
        current_code_data = code_list[0]
    
    # print(current_code_data)

    data = []
    for item in current_code_data["response"]:
        key = item["key"]

        print("Searching for", key, "in NOTAM cache...")
        key_notam = list(db.cache_notams.find({'key':key}))

        if len(key_notam) == 0:
            print("Key", key, "not found in NOTAM cache. Scraping...")
            raw_message = item["all"]
            notam_decoded = find_insights(raw_message)
            
            if sub == "ALL" or notam_decoded["Subject"] == sub:
                data.append(notam_decoded)
            

            db.cache_notams.insert_one({'key': key, 'notam': notam_decoded})

            cache_subjects = list(db.cache_subjects.find({
                "icao_code" : notam_decoded["ICAO_Code"],
                "subject" : notam_decoded["Subject"]
            }))
            print(cache_subjects)

            if len(cache_subjects) == 0:
                db.cache_subjects.insert_one({
                    "icao_code" : notam_decoded["ICAO_Code"],
                    "subject" : notam_decoded["Subject"]
                })
        
        else:
            print("Key", key, "found in NOTAM cache.")
            if sub == "ALL" or key_notam[0]["notam"]["Subject"] == sub:
                data.append(key_notam[0]["notam"])
        
        print("---")
    
    unique_subjects = list(db.cache_subjects.find({
        "icao_code" : code
    }))

    return jsonify({
        "unique_subjects": [x["subject"] for x in unique_subjects],
        "data": data,
        "code": code
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6942,debug=False)