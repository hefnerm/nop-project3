
#input: dictionaries containing the train information and the powerpofiles of each leg in the form of the return of the readInstance function of readWrite.py
#output: T_m: the planning horizon as a list of minutes; PL: a dictionary containing for each LegID its prior leg; ST: a dictionary containing for each leg its direct successor (chronological) leg on the same track; passConOrd: a list of every two legs that form a passenger connection, the first leg is the incoming leg and the second is the outgoing leg (end station of the first and start station of the second are equal); timeHorizonMinutes: the planning Horizon in minutes as integer; newPowerDic: the input powerDic in a new format, containing the powerprofile of each LegId
def getSets(trainDic, powerDic):
	
	#the planning horizon is the maximal time a train can ride, so the maximum of latest departure time + travel time
	timeHorizonMinutes = 0
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			leg['TrainID'] = train['TrainID']
			if leg['LatestDepartureTime'] + leg['TravelTime'] > timeHorizonMinutes:
				timeHorizonMinutes = leg['LatestDepartureTime'] + leg['TravelTime']
	
	T_m = range(0, timeHorizonMinutes + 1)
	
	#for each leg there can only be one unique prior leg from the same train
	PL = {}
	for train in trainDic['Trains']:
		legList = train['Legs'].copy()
		for leg in train['Legs']:
			for leg2 in legList:
				if leg['EndStationID'] == leg2['StartStationID']:
					PL[leg2['LegID']] = leg
					break
	
	legs = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legs.append(leg)
	
	#for each leg the successor leg is already determined by the current departure times
	ST = {}
	legCopy = legs.copy()
	for leg in legs:
		#minCurDepTime saves the minimal time of a successor leg on the same track
		minCurDepTime = None
		for leg2 in legCopy:
			if leg['TrackID'] == leg2['TrackID']:
				if minCurDepTime == None:
					if leg2['CurrentDepartureTime'] > leg['CurrentDepartureTime']:
						ST[leg['LegID']] = leg2
						minCurDepTime = leg2['CurrentDepartureTime']
				else:
					if leg2['CurrentDepartureTime'] > leg['CurrentDepartureTime'] and leg2['CurrentDepartureTime'] < minCurDepTime:
						ST[leg['LegID']] = leg2
						minCurDepTime = leg2['CurrentDepartureTime']
		
		#save if a leg does not have a chronological successor
		if minCurDepTime == None:
			ST[leg['LegID']] = False
	
	#legs l1 and l2 form a passenger connection iff l1 ends in the same station l2 starts and the difference of the current departure time of l2 and the arriving time of l1 is between 5 and 15 minutes
	passConOrd = []
	for leg1 in legs:
		for leg2 in legCopy:
			if leg1['EndStationID'] == leg2['StartStationID'] and not leg1['TrainID'] == leg2['TrainID']:
				if 5 <= -(leg1['CurrentDepartureTime'] + leg1['TravelTime']) + leg2['CurrentDepartureTime'] <= 15:
					if not (leg2['LatestDepartureTime'] - (leg1['EarliestDepartureTime'] + leg1['TravelTime']) <= 15 and 5 <= leg2['EarliestDepartureTime'] - (leg1['LatestDepartureTime'] + leg1['TravelTime'])):
						passConOrd.append([leg1, leg2])
	
	#save the powerprofile dictionary in a new format for easier access for every legID
	newPowerDic = {}
	for profile in powerDic['Powerprofiles']:
		newPowerDic[profile['LegID']] = profile['Powerprofile']
	
	return T_m, PL, ST, passConOrd, timeHorizonMinutes, newPowerDic

#input: trainDic containg all train and leg information, especially the earliest departure time and the latest departure time for each leg
#output: trainDic only changed the earliest and latest departure times

def newELDepTimes(trainDic):
	
	#for every train the earliest departure time of a leg has to bigger or equal than the earliest departure time of the leg 
	#before plus the minimum stopping time plus traveltime
	for train in trainDic['Trains']: 
		for i in range(1,len(train['Legs'])):
			train['Legs'][i]['EarliestDepartureTime']=max(train['Legs'][i]['EarliestDepartureTime'], train['Legs'][i-1]['EarliestDepartureTime'] + train['Legs'][i-1]['MinimumStoppingTime'] + train['Legs'][i-1]['TravelTime'] )
	
	#for every train the latest departure time of a leg i has to be smaller or equal than the latest departuretime of the leg after i+1
	# minus the minimum stopping time of i minus the traveltime 
	for train in trainDic['Trains']:
		for i in reversed(range(0,len(train['Legs'])-1)):
			train['Legs'][i]['LatestDepartureTime']=min(train['Legs'][i]['LatestDepartureTime'], train['Legs'][i+1]['LatestDepartureTime'] - train['Legs'][i]['MinimumStoppingTime'] - train['Legs'][i]['TravelTime'] )
