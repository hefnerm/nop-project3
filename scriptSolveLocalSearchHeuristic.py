import readWrite
import preprocess
import time
import localSearchHeuristic

pcoCorrect = False
requiredDecrease = 1
timeLimit = 18000

for instance in [1]:
	
	trainDic, powerDic = readWrite.readInstance(instance)
	preprocess.newELDepTimes(trainDic)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic, pcoCorrect)
	
	print("\ninstance ", instance, ", required decrease ", requiredDecrease)
	
	x, maxIndex, maxVal = localSearchHeuristic.local_search(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, timeLimit, instance, requiredDecrease, pcoCorrect)