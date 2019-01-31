import readWrite
import preprocess
import time
import localSearchHeuristic

#pcoCorrect is a boolean that is true, if the heuristic shall work with the correct PCOs, and false, if it shall also consider legs with the same trainIDs as a passenger connection
pcoCorrect = True
#the factor by which we require an improvement of the solution
requiredDecrease = 1
timeLimit = 18000

for instance in [1, 7, 9, 10]:
	
	trainDic, powerDic = readWrite.readInstance(instance)
	preprocess.newELDepTimes(trainDic)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic, pcoCorrect)
	
	print("instance ", instance, ", required decrease ", requiredDecrease)
	
	localSearchHeuristic.local_search(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, timeLimit, instance, requiredDecrease, pcoCorrect)