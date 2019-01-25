from gurobipy import *
import math
import time
import json
import random

run_time = 18000

#input: trainDic: a dictionary containing all train information in the format of the return of readInstance readWrite.py and a leg
#output: true, if the leg is the starting leg of a train (the leg has no prior leg) or false otherwise
def legHasNoPredec(trainDic, leg):
	
	for train in trainDic['Trains']:
		if leg == train['Legs'][0]:
			return True
	
	return False

def solve_min_heuristic(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin, instance):
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)

	TLegs = {}
	for j in legList:
		TLegs[j['LegID']] = range(j['EarliestDepartureTime'], j['LatestDepartureTime'] + 1)
	
	model = Model("Heuristic model for lower bound for energy efficient train timetable problem")
	
	#model.Params.timelimit = 3600
	#model.Params.mipGap = 0.000001
	#model.Params.BestBdStop = upper_bound

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
		with open('./solutions_min_heuristic/solution_min_heuristic_instance_' + str(instance) + '.json.txt', 'w', encoding='utf-8') as outfile:
			json.dump(solution, outfile)
	except:
		print("solutionfile could not be created!")
		exit()

def min_heuristic(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin, instance):
	
	start_time = time.time()
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	k = len(PassConOrd)
	#n = random.randint(1, k+1)
	
	subsetPassConOrd = []
	#subsetPassConOrd = random.sample(PassConOrd, int(k/2))
	
	#for [i, j] in subsetPassConOrd:
	#	print(i['LegID'], j['LegID'])
	
	
	model, x, a, I, maxVal, TLegs = solve_min_heuristic(trainDic, powerDic, T_m, PL, ST, subsetPassConOrd, timeHorizonMin, instance)
	
	elapsed_time = time.time() - start_time
	maxIndex = -1
	
	#oldModel = None
	#oldX = None
	#oldTLegs = None
	
	#while elapsed_time < run_time:
	#	print("maxVal: ", maxVal)
	#	prevMax = maxVal
	#	prevI = I
		
	#	model, x, a, I, maxVal, TLegs = solve_heuristic(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin, instance)
		
		
		#infeasible
		#if model.status in [3, 15]:
		#	intervalRange += 1
		#	fixedLegs, variableLegs = getFixedLegs(legList, legDepartureTime, fixedTimes, maxIndex, intervalRange)
		#	I = prevI
		#	
		#	elapsed_time = time.time() - start_time
		#	continue
		
		#timelimit reached
		#if model.status == 9:
		#	if len(I) > 0:
		#		createSolution(model, x, TLegs, legList, instance, "timelimit in model reached!")
		#	else:
		#		createSolution(oldModel, oldX, oldTLegs, legList, instance, "timelimit in model reached!")
		#	break
		
		#keyboard interrupt
		#if model.status == 11:
		#	if len(I) > 0:
		#		createSolution(model, x, TLegs, legList, instance, "keyboard interrupt; no upper bound found, old solution created")
		#	else:
		#		createSolution(oldModel, oldX, oldTLegs, legList, instance, "keyboard interrupt; no upper bound found, old solution created")
		#	break
		
	#	oldModel = model
	#	oldX = x
	#	oldTLegs = TLegs
		
		
	#	elapsed_time = time.time() - start_time
	
	#if elapsed_time >= run_time:
	#	createSolution(oldModel, oldX, oldTlegs, instance, "timelimit reached!")
	
	return x, maxIndex, maxVal