import readWrite
import preprocess
import modelEETT
import curMaximum
import time

file=open("Laufzeiten.txt","w")

for instance in range(7,8):
	start_time = time.time()

	trainDic, powerDic = readWrite.readInstance(instance)
	T_m, PL, ST, passConOrd, timeHorizonMin, newPowerDic = preprocess.getSets(trainDic, powerDic)
	newTrainDic = preprocess.newEL(trainDic)


	model, x, a, I, maximum = modelEETT.solve_EETT(newTrainDic, newPowerDic, T_m, PL, ST, passConOrd, timeHorizonMin,instance)

	elapsed_time = time.time() - start_time
	print('instance:', instance, 'time:', elapsed_time)
	
	#save the time
	file.write('instance: ')
	file.write(str(instance))
	file.write(' time: ')
	file.write(str(elapsed_time))

file.close
