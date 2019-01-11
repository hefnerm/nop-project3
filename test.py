import readWrite
import preprocess
import modelEETT
import curMaximum

trainDic, powerDic = readWrite.readInstance(1)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)


model, x, I, maximum = modelEETT.solve_EETT(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin)
