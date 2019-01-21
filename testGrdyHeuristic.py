import readWrite
import preprocess
import curMaximum
import time
import grdy_heuristic

instance = 2

trainDic, powerDic = readWrite.readInstance(instance)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
newTrainDic = preprocess.newEL(trainDic)

x, maxIndex, maxVal = grdy_heuristic.greedy_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance)