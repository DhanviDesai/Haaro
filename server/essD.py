#!/bin/python
import requests
import random
import json
import re
from flask import Flask
from flask import request
from ICAO import acronyms as abbrs
import pandas


def unabbreviate_tams ( notam ):

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
    return op.capitalize()



def gettams(api_key, states, notam_type, arrival,departure):

	api_key = '8ea8c220-3859-11e9-9265-5985bd35eb75'
	states = 'IND'
	notam_type = 'airport'
	req_url = 'https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/states/notams/notams-list?format=json&api_key={0}&states={1}&type={2}&locations={3},{4}'.format(
            api_key, states, notam_type, arrival,departure);
	resp = requests.get(req_url)
	if resp.status_code != 200:
		# This means something went wrong.
		raise ApiError('GET / {}'.format(resp.status_code))
	notams = []
	print(resp.json)
	for notam in resp.json():
		# Process each NOTAM here

        	# Calculate Priority
		notam['priority'] = random.random()
		notams.append(notam)
	return notams


def getSimplified(notam):
	print(0)
	api_key = '8ea8c220-3859-11e9-9265-5985bd35eb75'
	req_url='https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/states/notams/qcode-stats?format=json&notam={0}&api_key={1}'.format(notam,api_key)
	resp = requests.get(req_url)
	if resp.status_code != 200:
		raise ApiError('GET / {}'.format(resp.status_code))

	d={}
	for detail in resp.json():
		s=detail['meaning']
		s.replace('Some','')
		d['notam']=detail['notam']
		d['meaning'] = s
		d['area']=detail['area_signification']
		d['subarea']=detail['subarea']
	return d



def freeClutter(notams):
	details = []
	for i in range(len(notams)):
		notam=notams[i]
		d={}
		if(notam['SubArea']!= '' or notam['Area']!= '' or notam['Subject']!= ''):
			d['subarea']=notam['SubArea']
			d['area']=notam['Area']
			d['subject']=notam['Subject']
			d['message']=unabbreviate_tams(notam)
			details.append(d)
	return details

df=pandas.read_csv('airport_codes_list.csv',encoding = "ISO-8859-1")
df.dropna()

def convertIcao(iata):
	d={}
	df2 =df.loc[(df['IATA']==iata) | (df['ICAO']==iata)]
	s=df2.iloc[:,1:3]
	d['code']=s.values[0][0]
	d['name']=s.values[0][1]
	return d



app = Flask(__name__)
@app.route("/", methods=['GET'])
def a1():
	details=[]
	notams = gettams('a', 'b', 'c', 'd','e')
	for notam in notams:
		detail = getSimplified(notam)
		details.append(detail)
        	#if notam['Modifier'] == 'Plain Language':
           	# print (notam['message'])
        	#else :
            	#print( "~~~~~", notam['message'])
		#print('\n\n')
	return json.dumps(details)


@app.route("/notams",methods=['GET'])
def a3():
	start = int(request.args.get('start'))
	end = int(request.args.get('end'))
	arrival = request.args.get('arrival')
	departure = request.args.get('departure')
	notams = gettams('a','b','c	',arrival,departure)
	detail = freeClutter(notams)
	return json.dumps(detail)	


@app.route("/flights",methods=['GET'])
def a5():
	airline = request.args.get('airline')
	api_key='69397a-7a4d8d'
	req_url='http://aviation-edge.com/v2/public/flights?key={0}&airlineIcao={1}'.format(api_key,airline)
	resp = requests.get(req_url)
	details=[]
	for flight in resp.json():
		final={}
		arr=flight['arrival']
		iata=arr['icaoCode']
		df2=df.loc[(df['IATA']==iata)|(df['ICAO']==iata)]
		s=df2.iloc[:,1:3]
		final['arrivalCode']=s.values[0][0]
		final['arrivalName']=s.values[0][1]
		dept=flight['departure']
		iata=dept['icaoCode']
		df2=df.loc[(df['IATA']==iata)|(df['ICAO']==iata)]
		s=df2.iloc[:,1:3]
		final['departureCode']=s.values[0][0]
		final['departureName']=s.values[0][1]
		air=flight['aircraft']
		final['regnumber']=air['regNumber']
		final['status']=flight['status']
		details.append(final)
	return json.dumps(details)

@app.route("/airports",methods=['GET'])
def a9():
	details=[]
	for i in range(len(df)):
		data = df.iloc[i]
		d={}
		d['code']=data.loc['ICAO']
		d['name']=data.loc['Name']
		details.append(d)
	return json.dumps(details)


@app.route("/airlines",methods=['GET'])
def a4():
		api_key = '8ea8c220-3859-11e9-9265-5985bd35eb75'
		req_url = 'https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/airlines/designators/iosa-registry-list?format=json&api_key={0}'.format(api_key)
		resp = requests.get(req_url)
		details = []
		for airline in resp.json():
			d={}
			d['name']=airline['operatorName']
			d['code']=airline['operatorCode']
			details.append(d)
		return json.dumps(details)

@app.route("/weather",methods=['GET'])
def a6():
	api_omp='747981cc2437283039626d3c143ff0b2'
	api_key='8ea8c220-3859-11e9-9265-5985bd35eb75'
	departure=request.args.get('dept')
	arrival=request.args.get('arri')
	req_url='https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/airports/weather/current-conditions-list?format=json&api_key={0}&airports={1},{2}'.format(api_key,departure,arrival)
	resp = requests.get(req_url)
	details=[]
	for airport in resp.json():
		d={}
		d['airport']=airport['airport']
		d['precipitaion']=airport['precipitation']
		lat=airport['latitude']
		lon=airport['longitude']
		req_url_omp='https://api.openweathermap.org/data/2.5/weather?appid={0}&lat={1}&lon={2}'.format(api_omp,lat,lon)
		respomp = requests.get(req_url_omp)
		data=respomp.json()
		we=data['weather']
		for i in range(len(we)):
			w=we[i]
			d['description']=w['description']
		main=data['main']
		d['temp']=main['temp']
		d['humidity']=main['humidity']
		d['min']=main['temp_min']
		d['max']=main['temp_max']
		d['visibility']=data['visibility']
		wind=data['wind']
		d['wind']=wind['speed']
		details.append(d)
	return json.dumps(details)



@app.route("/useful",methods=['GET'])
def a2():
	s = request.args.get('id')
	print(s)
	return s

if __name__ == '__main__':
    app.run(host='0.0.0.0')
