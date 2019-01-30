import readWrite
import preprocess
import modelEETTStartSolution
import time

instance = 1

start_time = time.time()

#read and preprocess the data
trainDic, powerDic = readWrite.readInstance(instance)
preprocess.newELDepTimes(trainDic)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)

#solve the model
model, x, a, I, maximum = modelEETTStartSolution.solve_EETT(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin, instance)

elapsed_time = time.time() - start_time
print('instance:', instance, 'time:', elapsed_time)
