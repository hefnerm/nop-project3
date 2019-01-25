import readWrite
import preprocess
import first_idea_min_heuristic

instance = 1

trainDic, powerDic = readWrite.readInstance(instance)
preprocess.newELDepTimes(trainDic)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)


x, maxIndex, maxVal = first_idea_min_heuristic.min_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance)