def getSets(trainDic, powerDic):
	timeHorizonMinutes = 0
	
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			if leg['LatestDepartureTime'] + leg['TravelTime'] > timeHorizonMinutes:
				timeHorizonMinutes = leg['LatestDepartureTime'] + leg['TravelTime']
	
	T_m = range(0, timeHorizonMinutes + 1)
	
	PL = {}
	
	for train in trainDic['Trains']:
		legList = train['Legs'].copy()
		for leg in train['Legs']:
			for leg2 in legList:
				if leg['EndStationID'] == leg2['StartStationID']:
					PL[leg2['LegID']] = leg
					break
	
	ST = {}
	
	legs = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legs.append(leg)
	
	legCopy = legs.copy()
	for leg in legs:
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
		
		if minCurDepTime == None:
			ST[leg['LegID']] = False
	
	passConOrd = []
	
	for leg1 in legs:
		for leg2 in legCopy:
			if leg1['EndStationID'] == leg2['StartStationID']:
				if 5 <= -(leg1['CurrentDepartureTime'] + leg1['TravelTime']) + leg2['CurrentDepartureTime'] <= 15:
					passConOrd.append([leg1, leg2])
	
	newPowerDic = {}
	for profile in powerDic['Powerprofiles']:
		newPowerDic[profile['LegID']] = profile['Powerprofile']
	
	return T_m, PL, ST, passConOrd, timeHorizonMinutes, newPowerDic

