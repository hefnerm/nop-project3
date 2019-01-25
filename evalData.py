import readWrite
import preprocess
for instance in range(1, 11):
	trainDic, powerDic = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	newTrainDic = preprocess.newELDepTimes(trainDic)
	
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
		elif 5 <= abs(j['LatestDepartureTime'] - (i['EarliestDepartureTime'] + i['TravelTime'])) <= 15 and 5 <= abs(j['EarliestDepartureTime'] - (i['LatestDepartureTime'] + i['TravelTime'])) <= 15:
			amountReallyRedundantCon += 1
	
	print(len(passConOrd), nFalsePassCon, amountReallyRedundantCon, "\n")