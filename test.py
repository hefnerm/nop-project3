import readWrite
import preprocess
import modelEETT
import curMaximum

trainDic, powerDic = readWrite.readInstance(1)
T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)

max, I = curMaximum.computeCurrentMaximum(1)
print(max, I)


#model, x, I, av = modelEETT.solve_EETT(trainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin)
#print("T_m: ", T_m)
#print("\nPL: ", PL)
#print("\nST: ", ST)
#print("\nPassConOrd:", PassConOrd)