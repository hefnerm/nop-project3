import readWrite
import preprocess
import modelEETT
import curMaximum
import time
import modelEETTnewLucia

file=open("solution_everything.txt","w")

for instance in range(3,4):
	start_time = time.time()

	trainDic, powerDic = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	newTrainDic = preprocess.newEL(trainDic)


	model, x, a, I, maximum = modelEETTnewLucia.solve_EETT(newTrainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin,instance)

	elapsed_time = time.time() - start_time
	print('instance:', instance, 'time:', elapsed_time)
	
	#save the time and solutions
	file.write('instance: ')
	file.write(str(instance))
	file.write(' time: ')
	file.write(str(elapsed_time))
	file.write(' ObjVal: ')
	file.write(str(model.ObjVal))
	file.write(' LowerBound: ')
	file.write(str(model.ObjBound))
	file.write(' GAP: ')
	file.write(str(model.MIPGap))
	file.write('\n')
file.close
