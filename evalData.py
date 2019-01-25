import readWrite
import preprocess
for instance in range(1, 11):
	trainDic, powerDic = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	newTrainDic = preprocess.newELDepTimes(trainDic)
	
	print(instance, "\n")
	
	amountRedundantCon = 0
	for [i, j] in passConOrd:
		if j['LatestDepartureTime'] - i['EarliestDepartureTime'] <= 15 and j['EarliestDepartureTime'] - i['LatestDepartureTime'] >= 5:
			amountRedundantCon += 1
			#print(i)
			#print(j, "\n")
	
	print(len(passConOrd), amountRedundantCon, "\n")