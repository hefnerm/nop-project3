from gurobipy import *
import curMaximum
import math
import time
import json

run_time = 180

#input: trainDic: a dictionary containing all train information in the format of the return of readInstance readWrite.py and a leg
#output: true, if the leg is the starting leg of a train (the leg has no prior leg) or false otherwise
def legHasNoPredec(trainDic, leg):
	
	for train in trainDic['Trains']:
		if leg == train['Legs'][0]:
			return True
	
	return False

def solve_heuristic(trainDic, powerDic, fixedLegs, fixedTimes, T_m, PL, ST, PassConOrd, timeHorizonMin, instance, upper_bound):
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)

	TLegs = {}
	for j in legList:
		TLegs[j['LegID']] = range(j['EarliestDepartureTime'], j['LatestDepartureTime'] + 1)
	
	model = Model("Greedy heuristic model for energy efficient train timetable problem")
	
	#model.Params.timelimit = 3600
	#model.Params.mipGap = 0.000001
	model.Params.BestBdStop = upper_bound

	model.modelSense = GRB.MINIMIZE

	#variables
	
	x = {}
	#x[j, t] = 1 if the leg j departs at minute t, 0 otherwise
	for j in legList:
		for t in TLegs[j['LegID']]:
			x[j['LegID'], t] = model.addVar(vtype=GRB.BINARY, obj=0.0, name="x_" + str(j['LegID']) + "_" + str(t))
	
	a = {}
	#a[tau] is the nonnegative poweramount of the whole system at second tau
	for tau_m in T_m:
		for tau in range(60*tau_m, 60*tau_m + 60):
			a[tau] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=0.0, name="a_" + str(tau))
	
	I = {}
	#I[i] is the average powerconsumption in the i'st interval
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		I[i] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=0.0, name="I_" + str(i))
	
	#maximum forms the value of the maximal interval
	maximum = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=1.0, name="maximum")
	
	model.update()
	
	#constraints
	
#	(1) #theoretisch unnoetig nur zur fehlervermeidung
#	for i in legList:
#		model.addConstr(i['EarliestDepartureTime'] <= quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]))
#		model.addConstr(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) <= i['LatestDepartureTime'])
	
	for j in fixedLegs:
		model.addConstr(x[j['LegID'], fixedTimes[j['LegID']]] == 1)
	
	#(2)
	for j in legList:
		if not legHasNoPredec(trainDic, j):
			i = PL[j['LegID']]
			model.addConstr(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime'] + i['MinimumStoppingTime'] <= quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]))
	
	#(3)
	for j in legList:
		if not ST[j['LegID']] == False:
			i = ST[j['LegID']]
			model.addConstr(quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]) + j['MinimumHeadwayTime'] <= quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]))
	
	#(4)
	for [i, j] in PassConOrd:
		model.addConstr(5 <= -(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]))
		model.addConstr(-(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]) <= 15)
	
	#(5)
	for j in legList:
		model.addConstr(quicksum(x[j['LegID'], t] for t in TLegs[j['LegID']]) == 1)
	
	#(6)
	for tau_m in T_m:
		legSet = []
		for leg in legList:
			if leg['EarliestDepartureTime'] <= tau_m <= leg['LatestDepartureTime'] + leg['TravelTime']:
				legSet.append(leg)
		
		for tau in range(60*tau_m, 60*tau_m + 60):
			if tau - 60*tau_m > 0:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'] + 1, j['EarliestDepartureTime']), min(tau_m , j['LatestDepartureTime'] ) + 1)) for j in legSet))
			else:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'], j['EarliestDepartureTime']), min(tau_m, j['LatestDepartureTime']) + 1)) for j in legSet))
	
	#(7)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(I[i] == (quicksum(a[tau] for tau in range(15*(i-1)*60 + 1, min(15*i*60 - 1 + 1, timeHorizonMin*60))) + a[15*(i-1)*60]/2 + a[min(15*i*60, timeHorizonMin*60 + 1)]/2 )/900)
	
	
	#(8)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(maximum >= I[i])
	
	#if upper_bound > 0:
	#	model.addConstr(maximum <= 0.9999*upper_bound)
	
	model.optimize()
	
	Ireturn = []
	if not model.status in [3, 9, 11, 15]:
		for i in I:
			Ireturn.append(I[i].X)
		maxReturn = max(Ireturn)
		
	elif model.status in [9, 11]:
		try:
			for i in I:
				Ireturn.append(I[i].UB)
			maxReturn = maximum.UB
		except:
			maxReturn = 0
	else:
		maxReturn = 0
	
	return model, x, a, Ireturn, maxReturn, TLegs

def setCurDepTimes(legList, maxIndex):
	fixedLegs = []
	variableLegs = []
	fixedTimes = {}
	for leg in legList:
		if leg['CurrentDepartureTime'] <= 15*(maxIndex - 1) <= leg['CurrentDepartureTime'] + leg['TravelTime'] or 15*(maxIndex - 1) <= leg['CurrentDepartureTime'] <= 15*(maxIndex + 1 + 1) or leg['CurrentDepartureTime'] <= 15*(maxIndex + 1 + 1) <= leg['CurrentDepartureTime'] + leg['TravelTime']:
			variableLegs.append(leg)
		else:
			fixedLegs.append(leg)
			fixedTimes[leg['LegID']] = leg['CurrentDepartureTime']
	
	return fixedLegs, fixedTimes, variableLegs

def getFixedLegs(legList, legDepartureTime, fixedTimes, maxIndex, intervalRange):
	fixedLegs = []
	variableLegs = []
	for j in legList:
		if legDepartureTime[j['LegID']] <= 15*(maxIndex - intervalRange) <= legDepartureTime[j['LegID']] + j['TravelTime'] or 15*(maxIndex - intervalRange) <= legDepartureTime[j['LegID']] <= 15*(maxIndex + 1 + intervalRange) or legDepartureTime[j['LegID']] <= 15*(maxIndex + 1 + intervalRange) <= legDepartureTime[j['LegID']] + j['TravelTime']:
			variableLegs.append(j)
		else:
			fixedLegs.append(j)
			fixedTimes[j['LegID']] = legDepartureTime[j['LegID']]
	
	return fixedLegs, variableLegs

def createSolution(model, x, TLegs, legList, instance, string):
	print(string)
	print("best objective: ", model.ObjVal)
	solution = { "Legs": {}}
	try:
		for j in legList:
			for t in TLegs[j['LegID']]:
				if x[j['LegID'], t].X > 0.5:
					solution["Legs"][j['LegID']] = t
	except:
		for j in legList:
			for t in TLegs[j['LegID']]:
				if x[j['LegID'], t].UB > 0.5:
					solution["Legs"][j['LegID']] = t
	try:
		with open('./solutions_greedy_heuristic/solution_greedy_heuristic_instance_' + str(instance) + '.json.txt', 'w', encoding='utf-8') as outfile:
			json.dump(solution, outfile)
	except:
		print("solutionfile could not be created!")
		exit()

def greedy_heuristic(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin, instance):
	
	start_time = time.time()
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	intervalRange = 1
	
	maxVal, I = curMaximum.computeCurrentMaximum(instance)
	for index, m in enumerate(I):
		if m == maxVal:
			maxIndex = index
			break
	
	fixedLegs, fixedTimes, variableLegs = setCurDepTimes(legList, maxIndex)
	
	elapsed_time = time.time() - start_time
	
	oldModel = None
	oldX = None
	oldTLegs = None
	
	while elapsed_time < run_time:
		print("\nargMax: ", maxIndex)
		print("maxVal: ", maxVal)
		print("I: ", I)
		print("intervalRange: ", intervalRange)
		print("nrFixedLegs: ", len(fixedLegs))
		print("nrVarLegs: ", len(variableLegs),"\n")
		prevMax = maxVal
		prevI = I
		if maxVal <= 0:######################################################################DELETE THIS
			Error("THIS SHOULD NOT HAPPEN!")
		
		model, x, a, I, maxVal, TLegs = solve_heuristic(trainDic, powerDic, fixedLegs, fixedTimes, T_m, PL, ST, PassConOrd, timeHorizonMin, instance, maxVal)
		
		if maxVal == 0:
			maxVal = prevMax
		
		#infeasible
		if model.status in [3, 15]:
			intervalRange += 1
			fixedLegs, variableLegs = getFixedLegs(legList, legDepartureTime, fixedTimes, maxIndex, intervalRange)
			I = prevI
			
			elapsed_time = time.time() - start_time
			continue
		
		#timelimit reached
		if model.status == 9:
			if len(I) > 0:
				createSolution(model, x, TLegs, legList, instance, "timelimit in model reached!")
			else:
				createSolution(oldModel, oldX, oldTLegs, legList, instance, "timelimit in model reached!")
			break
		
		#keyboard interrupt
		if model.status == 11:
			if len(I) > 0:
				createSolution(model, x, TLegs, legList, instance, "keyboard interrupt; no upper bound found, old solution created")
			else:
				createSolution(oldModel, oldX, oldTLegs, legList, instance, "keyboard interrupt; no upper bound found, old solution created")
			break
		
		oldModel = model
		oldX = x
		oldTLegs = TLegs
		
		for index, m in enumerate(I):
			if m == maxVal:
				newMaxIndex = index
				break
		
		if newMaxIndex == maxIndex:
			if maxIndex - intervalRange <= 0 and maxIndex + intervalRange >= len(I):
				elapsed_time = time.time() - start_time
				createSolution(model, x, TLegs, legList, instance, "optimal solution found! \n time: " + str(elapsed_time) + "s")
				break
			
			intervalRange += 1
		else:
			intervalRange = 1
		
		maxIndex = newMaxIndex
		
		legDepartureTime = {}
		
		for j_id, t in x:
			if x[j_id, t].X == 1:
				legDepartureTime[j_id] = t
		
		fixedLegs, variableLegs = getFixedLegs(legList, legDepartureTime, fixedTimes, maxIndex, intervalRange)
		
		elapsed_time = time.time() - start_time
	
	if elapsed_time >= run_time:
		createSolution(oldModel, oldX, oldTLegs, legList, instance, "timelimit reached! ran " + str(elapsed_time) + "s")
	
	return x, maxIndex, maxVal