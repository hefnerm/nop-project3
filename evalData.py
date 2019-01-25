import readWrite
import preprocess
for instance in range(1, 11):
	trainDic, powerDic = readWrite.readInstance(instance)
	preprocess.newELDepTimes(trainDic)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	
	
	print(instance, "\n")
	
	amountRedundantCon = 0
	amountReallyRedundantCon = 0
	nFalsePassCon = 0
	#print(passConOrd)
	for [i, j] in passConOrd:
		if i['TrainID'] == j['TrainID']:
			#print("mst: ", i['MinimumStoppingTime'])
			print(i)
			print(j, "\n")
			nFalsePassCon += 1
		#if j['LatestDepartureTime'] - i['EarliestDepartureTime'] <= 15 and j['EarliestDepartureTime'] - i['LatestDepartureTime'] >= 5:
		#	amountRedundantCon += 1
		#	#print(i)
		#	#print(j, "\n")
		elif j['LatestDepartureTime'] - (i['EarliestDepartureTime'] + i['TravelTime']) <= 15 and 5 <= j['EarliestDepartureTime'] - (i['LatestDepartureTime'] + i['TravelTime']):
			amountReallyRedundantCon += 1
	
	print(len(passConOrd), amountReallyRedundantCon, "\n")