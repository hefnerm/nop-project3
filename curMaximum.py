import readWrite
import preprocess
import math

def computeCurrentMaximum(instance):
	trainDic, powerDicPrev = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, powerDic = preprocess.getSets(trainDic, powerDicPrev)
	
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	maxCurRidingTime = 0
	for leg in legList:
		if leg['CurrentDepartureTime'] + leg['TravelTime'] > maxCurRidingTime:
			maxCurRidingTime = leg['CurrentDepartureTime'] + leg['TravelTime']
	
	
	I = []
	
	a = []
	
	for tau_m in T_m:
		for tau in range(60*tau_m, 60*tau_m + 60):
			
			powerAtTau = 0
			for j in legList:
				if 60*j['CurrentDepartureTime'] <= tau <= 60*(j['CurrentDepartureTime'] + j['TravelTime']):
					powerAtTau = powerAtTau + powerDic[j['LegID']][tau - 60*j['CurrentDepartureTime']]
			
			a.append(powerAtTau)
	
	for i in range(1, math.floor(timeHorizonMin/15) + 1):
		intervalAverage = 0
		for tau in range(15*(i-1)*60 + 1, 15*i*60 - 1 + 1):
			intervalAverage = intervalAverage + a[tau]
		
		intervalAverage = (intervalAverage + a[15*(i-1)*60]/2 + a[15*i*60]/2)/900
		I.append(intervalAverage)
	
	if math.floor(timeHorizonMin/15) != timeHorizonMin/15:
		intervalLength = (timeHorizonMin - math.floor(timeHorizonMin/15)*15)*60
		intervalAverage = 0
		for tau in range(15*math.floor(timeHorizonMin/15)*60 + 1, 15*math.floor(timeHorizonMin/15)*60 + intervalLength):
			intervalAverage = intervalAverage + a[tau]
		
		intervalAverage = (intervalAverage + a[15*math.floor(timeHorizonMin/15)*60]/2 + a[15*math.floor(timeHorizonMin/15)*60 + intervalLength]/2)/intervalLength
		I.append(intervalAverage)
	
	maximum = max(I)
	
	return maximum, I

