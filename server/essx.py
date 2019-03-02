#!/bin/python
import requests
import random
import json
import re
import dateutil.parser
import time
from flask import Flask
import requests
import random
import json
import re
import dateutil.parser
import time
from flask import Flask, request, jsonify, json
from ICAO import acronyms as abbrs, entities as icao_entities, status as icao_status, entities_cat, status_cat
import mysql.connector as mariadb
from flask_cors import CORS
import pickle

from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np



def prioritize_tam( notam ):

    model   = pickle.load(open( 'lrm.sav', 'rb'))
    encoder = pickle.load(open( 'enc.sav', 'rb'))

    nid = notam['id']
    ent = notam['entity']
    loc = notam['location']
    sta = notam['status']

    yb = np.array( [ ent, loc, sta ]).reshape(1, -1)
    yt = encoder.transform(yb)
    val = model.predict(yt)[0][0] 
    return val


def process_tams ( notam ):

# ----------- Unabbreviate messages and store in "decoded"-------------

    message = notam["message"]
    message = re.sub( r"RWY([0-9/]+)", r"RWY \1", message)
    # message = re.sub( r"FLW:", r"FLW :", message)

    # Punctuations are a bitch sometimes
    message = re.sub( r"([,.:\"'-])", r" \1 " , message)

    # CREATED and SOURCE feilds need to GTFO
    message = re.sub( r'SOURCE ?: ?.*$', r'' , message)
    message = re.sub( r'CREATED ?: ?.*$', r'' , message)
    message = message.strip()

    words = re.findall(r'\S+|\n',message)

    trans = [abbrs.get( w.upper(), w ) for w in words]
    op = ' '.join(trans)
    op = re.sub( r" ([,.:\"']) ", r"\1", op)
    notam["decoded"] = op.capitalize()

# ------------ Translate "entity" and "status" ------------
    w = icao_entities.get( notam['entity'], notam['entity'] )
    notam["Subject"] = w
    w = icao_status.get( notam['status'], notam['status'] )
    notam["q_status"] = w.title()

# ------------ Translate "entity" and "status" categories ------------
    w = entities_cat.get( notam['entity'], notam['entity'] )
    notam["entity_category"] = w
    w = status_cat.get( notam['status'], notam['status'] )
    notam["status_category"] = w

# ------------ Extract coordinates using RegEx ------------

    regex = r'([0-9]+\.?[0-9]+)[NS]\s?([0-9]+\.?[0-9]+)[WE]'
    all_coordinates = re.findall(regex, notam["message"])
    if len(all_coordinates) != 0:
        notam["isCoordinates"] = True
    else:
        notam["isCoordinates"] = False
    notam["coordinates"] = all_coordinates


    return notam

def gettams( states, location, notam_type ): 

    mydb = mariadb.connect( host="localhost", user="pigeon", passwd="root", database="haro" ) 
    cursor = mydb.cursor() 
    query = '''
    SELECT EXISTS
    (
        SELECT * FROM notams
        WHERE
            UpdatedAt > ( DATE_SUB( NOW(), INTERVAL 3 HOUR ) )
        AND StateCode = %s
        AND location = %s
        AND type = %s
    )
    updated_recently
    '''

    cursor.execute(query, ( states, location, notam_type ))
    sql_result = cursor.fetchall()
    cursor.close()


    if sql_result[0][0] == 0:  # if not recently synchronized with API

        # Synchronize DB with API
        api_key = '9d849040-30e7-11e9-9872-b90b55b59c3d'
        req_url = 'https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/states/notams/notams-list?format=json&api_key={0}&states={1}&type={2}&locations={3}'.format( api_key, states, notam_type, location)
        resp = requests.get(req_url)

        if resp.status_code != 200:
            # This means something went wrong.
            raise ApiError('GET / {}'.format(resp.status_code))


        cursor = mydb.cursor() 
        for notam in resp.json():

            # Expand each abbreviations
            notam = process_tams(notam)

            tam_id        = notam["id"]
            entity        = notam["entity"]
            status        = notam["status"]
            Qcode         = notam["Qcode"]
            Area          = notam["Area"]
            SubArea       = notam["SubArea"]
            Condition     = notam["Condition"]
            Subject       = notam["Subject"]
            Modifier      = notam["Modifier"]
            message       = notam["message"]
            startdate     = notam["startdate"]
            enddate       = notam["enddate"]
            tam_all       = notam["all"]
            location      = notam["location"]
            isICAO        = notam["isICAO"]
            Created       = notam["Created"]
            key           = notam["key"]
            tam_type      = notam["type"]
            StateCode     = notam["StateCode"]
            StateName     = notam["StateName"]
            unabbr        = notam["decoded"]
            q_status      = notam["q_status"]
            ent_cat       = notam["entity_category"]
            stat_cat      = notam["status_category"]
            isCoordinates = notam["isCoordinates"]

            # Calculate Priority
            priority = float(prioritize_tam(notam))
            # print(priority)

            # Convert ISO 8601 timestamp to DateTime
            try: startdate = dateutil.parser.parse(startdate)
            except: startdate = ''
            try: enddate = dateutil.parser.parse(enddate)
            except: enddate = ''
            try: Created = dateutil.parser.parse(Created)
            except: Created = ''

            # Convert date time iso string
            try: str_startdate = startdate.strftime('%Y-%m-%d %H:%M:%S')
            except: str_startdate = ''
            try: str_enddate   = enddate.strftime('%Y-%m-%d %H:%M:%S')
            except: str_enddate   = ''
            try: str_Created   = Created.strftime('%Y-%m-%d %H:%M:%S')
            except: str_Created   = ''
                
# !!! UPSERT NOT INSERT!!!!

    # REPLACE into ... :/

            query = '''
REPLACE INTO notams (
    `id`, `entity`, `status`, `Qcode`, `Area`, `SubArea`, `Condition`,
    `Subject`, `Modifier`, `message`, `startdate`, `enddate`, `all`,
    `location`, `isICAO`, `Created`, `key`,`type`, `StateCode`,
    `StateName`, `decoded`, `priority`, `UpdatedAt`, `q_status`,
    `entity_category`, `status_category`, `isCoordinates`

)
VALUES (
	%s, %s, %s, %s, %s, %s, %s, 
	%s, %s, %s, %s, %s, %s, 
	%s, %s, %s, %s, %s, %s, 
	%s, %s, %s, NOW(), %s,
        %s, %s, %s
)
'''
            try:
                cursor.execute(query, ( tam_id, entity, status, Qcode, Area, SubArea, Condition, Subject, Modifier, message, str_startdate, str_enddate, tam_all, location, True, str_Created, key, tam_type, StateCode, StateName , unabbr, priority, q_status, ent_cat, stat_cat, isCoordinates))
            except:
                print(ent_cat, "   ")
                print(stat_cat, "   ")
                cursor.close()
                print("Error: {}".format('lmao'))
                break
        mydb.commit()

# !!! SYNC DONE RETRIEVE DATA AND SEND JSON FROM HERE !!!

    query = '''
    SELECT * from notams 
    WHERE StateCode = %s
        AND location = %s
        AND type = %s
        AND enddate > now()
    ORDER BY `priority` DESC, `Created` DESC
    '''

    cursor = mydb.cursor(dictionary=True) 
    cursor.execute( query, (states, location, notam_type, ) )
    results = cursor.fetchall()
    cursor.close()

    notams = []
    subjects = []

    for notam in results:
        tam                    = {}

        tam["id"]              = notam["id"]
        tam["entity"]          = notam["entity"]
        tam["status"]          = notam["status"]
        tam["Qcode"]           = notam["Qcode"]
        tam["Area"]            = notam["Area"]
        tam["SubArea"]         = notam["SubArea"]
        tam["Condition"]       = notam["Condition"]
        tam["Subject"]         = notam["Subject"]
        tam["Modifier"]        = notam["Modifier"]
        tam["message"]         = notam["message"]
        tam["all"]             = notam["all"]
        tam["location"]        = notam["location"]
        tam["isICAO"]          = notam["isICAO"]
        tam["key"]             = notam["key"]
        tam["type"]            = notam["type"]
        tam["StateCode"]       = notam["StateCode"]
        tam["StateName"]       = notam["StateName"]
        tam["message"]         = notam["message"]
        tam["priority"]        = notam["priority"]
        tam["decoded"]         = notam["decoded"]
        tam["q_status"]        = notam["q_status"]
        tam["entity_category"] = notam["entity_category"]
        tam["status_category"] = notam["status_category"]
        tam["isCoordinates"]   = notam["isCoordinates"]
        
        str_startdate =  notam["startdate"]
        str_enddate   =  notam["enddate"]
        str_Created   =  notam["Created"]

        try:
            str_startdate =  str_startdate.strftime('%Y-%m-%dT%H:%M:%SZ') 
        except:
            str_startdate = ''
        tam["startdate"] = str_startdate

        try:
            str_enddate   =  str_enddate.strftime('%Y-%m-%dT%H:%M:%SZ')   
        except:
            str_enddate   =  ''
        tam["enddate"] = str_enddate

        try:
            str_Created   =  str_Created.strftime('%Y-%m-%dT%H:%M:%SZ')   
        except:
            str_Created   =  ''
        tam["Created"] = str_Created
        # print ( tam['all'] , "\n\n--------\n\n" )
        # print ( tam['decoded'], "\n\n------------\n\n" )

        regex = r'([0-9]+\.?[0-9]+)[NS]\s?([0-9]+\.?[0-9]+)[WE]'
        all_coordinates = re.findall(regex, notam["message"])
        tam_coordinates = []
        for coordinates in all_coordinates:
            # print(coordinates[1])
            lat = coordinates[0]
            lon = coordinates[1]
            # if len(lat) <10
            lat_coor = lat[0:2] + " " + lat[2:4] + " " + lat[4:] 
            lon_coor = lon[0:3] + " " + lon[3:5] + " " + lon[5:]
            # lat = float(coordinates[0])
            # lon_coor = float(coordinates[0])

            # sec    = lat % 100
            # lat    = int(lat/100)
            # mins   = float( lat % 100 )
            # degree = int(lat/100)

            # lat_coor = degree + (mins/60) + (sec/3600)

            # sec    = lon % 100
            # lon    = int(lon/100)
            # mins   = float( lon % 100 )
            # degree = int(lon/100)

            # lon_coor = degree + (mins/60) + (sec/3600)

            print(type(lat))
            coordinate_tuple = { "lat" : lat_coor, "lng" : lon_coor }

            tam_coordinates.append( coordinate_tuple )
        # tam_coordinates = all_coordinates
        tam["coordinates"] = tam_coordinates

        subjects.append( tam['Subject'] )
        notams.append(tam)

    cursor.close()

    # remove duplicates from subjects
    subjects = list(set(subjects))
    dicti = {}
    for subject in subjects:
        arr = [ a for a in notams if a['Subject'] == subject ]
        dicti[subject] = arr

    return dicti , notams

def update_priorities ( contents ):
    mydb = mariadb.connect( host="localhost", user="pigeon", passwd="root", database="haro" ) 
    cursor = mydb.cursor() 
    query = """
CALL e_smooth ( %s, %s, 0.3 )
"""
    for feedback in contents:
        # print( feedback['id'], "  ", feedback['score'] )
        cursor.execute( query, ( feedback['id'], feedback['score'] ) )
    cursor.close()
    mydb.commit()
    # mariadb.close()


    # print( feedback['id'] 


app = Flask(__name__)
CORS(app)

@app.route("/lazy/<states>/<location>/<notam_type>", methods=['GET'])
def a1( states, location, notam_type ):
    dicti, notams = gettams( states, location, notam_type )
    return json.dumps({ 'notams' : notams, 'subjects' : dicti})

@app.route("/fetch/<states>/<location>/<notam_type>", methods=['GET'])
def a2( states, location, notam_type ):
    dicti, notams = gettams( states, location, notam_type )
    return json.dumps( notams )

@app.route("/feedback", methods=['POST'])
def b1():
    content = request.json
    update_priorities(content)
    return json.dumps({ 'message' : 'Okay thank you!' })

if __name__ == '__main__':
    app.run(host='0.0.0.0')
