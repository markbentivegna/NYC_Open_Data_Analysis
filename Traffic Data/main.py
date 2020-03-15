import csv 
import json
import operator
import requests
#This file was found at NYC Open Data
fields = [] 
rows = [] 
url = 'https://nyc-open-data-analysis.s3.amazonaws.com/Motor_Vehicle_Collisions_-_Crashes.csv'
with requests.Session() as s:
	download = s.get(url)
	decoded_content = download.content.decode('utf-8')
	csvreader = csv.reader(decoded_content.splitlines(), delimiter=',')
	fields = csvreader.__next__()
	for row in csvreader:
		rows.append(row)
	print("Total no. of rows: %d"%(len(rows))) 
	print('Field names are:' + ', '.join(field for field in fields))
injury_fields = ["NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED"]
#I found these fields to be either redundant or irrelevant so am ignoring them
ignore_fields = ["COLLISION_ID", "LATITUDE", "LONGITUDE", "NUMBER OF PERSONS INJURED", "NUMBER OF PERSONS KILLED", "NUMBER OF PEDESTRIANS INJURED", "NUMBER OF PEDESTRIANS KILLED", "NUMBER OF CYCLIST INJURED", "NUMBER OF CYCLIST KILLED", "NUMBER OF MOTORIST INJURED", "NUMBER OF MOTORIST KILLED"]
injury_columns = []
for i in range(len(fields)):
	if fields[i] in injury_fields:
		injury_columns.append(i)
factors_map = {}
current_factors = []
for row in rows:
	col_count = 0
	injury = False
	for index in injury_columns:
		if row[index]:
			if int(row[index]) > 0:
				injury = True
	for field in row:
		if field is not "" and fields[col_count] not in ignore_fields:
			current_factors.append(fields[col_count])
			if fields[col_count] not in factors_map:
				factors_map[fields[col_count]] = {}
			#I keep track of all features (or factors) in traffic accidents and the number of instances WITHOUT injuries and the instances WITH injuries
			if str(field) not in factors_map[fields[col_count]]:
				if injury:
					factors_map[fields[col_count]][str(field)] = [0, 1]
				else:
					factors_map[fields[col_count]][str(field)] = [1, 0]
			if fields[col_count] in factors_map and str(field) in factors_map[fields[col_count]]:
				if injury:
					factors_map[fields[col_count]][str(field)][1] += 1
				else:
					factors_map[fields[col_count]][str(field)][0] += 1
		col_count += 1

danger_ratio_map = {}
for factor in factors_map:
	danger_ratio = 0
	for field in factors_map[factor]:
		no_injuries = factors_map[factor][field][0]
		injuries = factors_map[factor][field][1]
		#If there are more than 50 instances of a feature involving an injury then I consider it significant 
		if injuries > 50:
			danger_ratio = injuries / (no_injuries + injuries)
			danger_ratio_map[field] = danger_ratio
dangerous_features = sorted(danger_ratio_map.items(), key=operator.itemgetter(1))
#The information is stored in results.json. The results are not clean or formatted
with open('results.json', 'w') as outfile:
    json.dump(dangerous_features, outfile)