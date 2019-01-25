import readWrite
import preprocess
import first_idea_min_heuristic

instance = 1

trainDic, powerDic = readWrite.readInstance(instance)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
newTrainDic = preprocess.newELDepTimes(trainDic)

x, maxIndex, maxVal = first_idea_min_heuristic.min_heuristic(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance)