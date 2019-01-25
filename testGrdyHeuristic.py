import readWrite
import preprocess
import curMaximum
import time
import grdy_heuristic

instance = 10

trainDic, powerDic = readWrite.readInstance(instance)
preprocess.newELDepTimes(trainDic)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)


x, maxIndex, maxVal = grdy_heuristic.greedy_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance)