import readWrite
import preprocess
import math

#input: instance number between 1 and 10
#output: the value of the current solution of the instance and a list of all interval values
def computeCurrentMaximum(instance, pcoCorrect=True):
	trainDic, powerDicPrev = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, powerDic = preprocess.getSets(trainDic, powerDicPrev, pcoCorrect)
	
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	I = []
	a = []
	
	for tau_m in T_m:
		for tau in range(60*tau_m, 60*tau_m + 60):
			#powerAtTau denotes the powerconsumption of the whole system at this second tau
			powerAtTau = 0
			for j in legList:
				#a train can only affect the powerconsumption if tau is during its riding time
				if 60*j['CurrentDepartureTime'] <= tau <= 60*(j['CurrentDepartureTime'] + j['TravelTime']):
					powerAtTau = powerAtTau + powerDic[j['LegID']][tau - 60*j['CurrentDepartureTime']]
			
			a.append(powerAtTau)
	
	#computing the average value for each interval of length 15 minutes
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		intervalAverage = 0
		for tau in range(15*(i-1)*60 + 1, min(15*i*60 - 1 + 1, timeHorizonMin*60)):
			intervalAverage = intervalAverage + max(a[tau],0)
		
		intervalAverage = (intervalAverage + max(a[15*(i-1)*60]/2,0) + max(a[min(15*i*60, timeHorizonMin*60 + 1)]/2,0))/900
		I.append(intervalAverage)
	
	maximum = max(I)
	
	return maximum, I

