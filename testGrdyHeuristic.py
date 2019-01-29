import readWrite
import preprocess
import curMaximum
import time
import grdy_heuristic

for instance in [9]:
	
	trainDic, powerDic = readWrite.readInstance(instance)
	preprocess.newELDepTimes(trainDic)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	
	print("\ninstance ", instance, ", required decrease 1")
	
	x, maxIndex, maxVal = grdy_heuristic.greedy_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance, 1)
	
	print("\ninstance ", instance, ", required decrease 0.9")
	
	x, maxIndex, maxVal = grdy_heuristic.greedy_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance, 0.9)