from gurobipy import *
import curMaximum
import math
import time
import json


#input: trainDic: a dictionary containing all train information in the format of the return of readInstance readWrite.py and a leg
#output: true, if the leg is the starting leg of a train (the leg has no prior leg) or false otherwise
def legHasNoPredec(trainDic, leg):
	
	for train in trainDic['Trains']:
		if leg == train['Legs'][0]:
			return True
	
	return False

def solve_heuristic(trainDic, powerDic, fixedLegs, fixedTimes, T_m, TLegs, PL, ST, PassConOrd, timeHorizonMin, instance, upper_bound, requiredDecrease, timeLimit):
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	model = Model("Greedy heuristic model for energy efficient train timetable problem")
	
	model.Params.timelimit = timeLimit
	#model.Params.mipGap = 0.000001
	if requiredDecrease == 1:
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
	
	#fix the legs that shall be fixed
	for j in fixedLegs:
		model.addConstr(x[j['LegID'], fixedTimes[j['LegID']]] == 1)
	
	#require an improvement of the solution
	if requiredDecrease != 1:
		model.addConstr(maximum <= requiredDecrease*upper_bound)
	
	#(M1)
	for j in legList:
		model.addConstr(quicksum(x[j['LegID'], t] for t in TLegs[j['LegID']]) == 1)
	
	#(M2)
	for j in legList:
		if not legHasNoPredec(trainDic, j):
			i = PL[j['LegID']]
			model.addConstr(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime'] + i['MinimumStoppingTime'] <= quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]))
	
	#(M3)
	for j in legList:
		if not ST[j['LegID']] == False:
			i = ST[j['LegID']]
			model.addConstr(quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]) + j['MinimumHeadwayTime'] <= quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]))
	
	#(M4)
	for [i, j] in PassConOrd:
		model.addConstr(5 <= -(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]))
		model.addConstr(-(quicksum(t*x[i['LegID'], t] for t in TLegs[i['LegID']]) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in TLegs[j['LegID']]) <= 15)
	
	#(M5)
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
	
	#(M6)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(I[i] == (quicksum(a[tau] for tau in range(15*(i-1)*60 + 1, min(15*i*60 - 1 + 1, timeHorizonMin*60))) + a[15*(i-1)*60]/2 + a[min(15*i*60, timeHorizonMin*60)]/2 )/900)
	
	#(M7)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(maximum >= I[i])
	
	model.optimize()
	
	#return variables: return a value of 0 if the model is interrupted by timelimit or keyboard
	Ireturn = []
	if not model.status in [3, 9, 11, 15]:
		for i in I:
			Ireturn.append(I[i].X)
		maxReturn = max(Ireturn)
		
	elif model.status in [9, 11]:
		try:
			if maximum.X < upper_bound:
				for i in I:
					Ireturn.append(I[i].X)
				maxReturn = maximum.X
			else:
				maxReturn = 0
				print("\nmaximum.X is equal to or larger than upper_bound; maximum.X: ", maximum.X, " upper_bound: ", upper_bound)
		except AttributeError:
			try:
				if maximum.UB < upper_bound:
					for i in I:
						Ireturn.append(I[i].UB)
					maxReturn = maximum.UB
				else:
					maxReturn = 0
					print("\nmaximum.UB is equal to or larger than upper_bound; maximum.UB: ", maximum.UB, " upper_bound: ", upper_bound)
			except AttributeError:
				maxReturn = 0
	else:
		maxReturn = 0
	
	return model, x, a, Ireturn, maxReturn

#input: legList a list containing all legs of the instance, maxIndex the number of the maximal interval
#output: for the original current departure times of the legs a list fixedLegs of all legs that shall be fixed, variableLegs that shall be variable and fixedTimes, a dictionary containing the fixed times for the fixed legs; all for an interval width of from 15 minutes before the interval of maxIndex until 15 minutes after that interval
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

#input: legList a list containing all legs of the instance, legDepartureTime a dictionary containing for every legID the current departure time, fixedTimes a dictionary, that will contain the new fixed times for the fixed legs, maxIndex the number of the maximal interval and intervalRange the number of intervals in front of and after the maximal interval, that shall be variable
#output: fixedLegs a list of all legs, that shall be fixed at the times in fixedTimes and variableLegs a list of all variable legs
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

#input: value the value of the solution that shall be created, x the x[j, t] decision variables, TLegs a dictionary containing all possible departure times for each leg, legList a list containing all legs of the instance, instance the number of the instance this heuristic is working on, requiredDecrease the factor <=1 of improvement, string a string that shall be printed on the console, pcoCorrect a boolean for if the heuristic shall consider the correct PCOs or shall also allow passenger connections between legs with same trainID
def createSolution(value, x, TLegs, legList, instance, requiredDecrease, string, pcoCorrect):
	print(string)
	print("best objective: ", value)
	solution = { "Legs": {}}
	try:
		for j in legList:
			for t in TLegs[j['LegID']]:
				#happens, if the solution to create is still the solution handed over
				if isinstance(x[j['LegID'], t], int):
					if x[j['LegID'], t] > 0.5:
						solution["Legs"][j['LegID']] = t
				else:
					if x[j['LegID'], t].X > 0.5:
						solution["Legs"][j['LegID']] = t
	#AttributeError if the access on the value of x throws an error
	except AttributeError:
		for j in legList:
			for t in TLegs[j['LegID']]:
				if x[j['LegID'], t].UB > 0.5:
					solution["Legs"][j['LegID']] = t
	try:
		if pcoCorrect:
			if requiredDecrease == 1:
				with open('./solutions_greedy_heuristic/solution_greedy_heuristic_instance_' + str(instance) + '.json.txt', 'w', encoding='utf-8') as outfile:
					json.dump(solution, outfile)
			else:
				with open('./solutions_greedy_heuristic_requiredDecrease/solution_greedy_heuristic_instance_' + str(instance) + '_rD.json.txt', 'w', encoding='utf-8') as outfile:
					json.dump(solution, outfile)
		else:
			with open('./solutions_greedy_heuristic_withError/solution_greedy_heuristic_instance_' + str(instance) + '_wE.json.txt', 'w', encoding='utf-8') as outfile:
				json.dump(solution, outfile)
	except:
		print("solutionfile could not be created!")
		exit()

#input: trainDic and powerDic dictionaries containing the train information and the powerpofiles of each leg in the form of the return of the preprocess function getSets, T_m a list of the time horizon in minutes, PL a dictionary containing for each legID the predecessor leg (if existing), ST a dictionary containing for each legID the successor train on the same track (if existing), PassConOrd a list of legs forming passenger connections, timeHorizonMin the time horizon in minutes (maximal value of T_m), timeLimit a time limit for the heuristic, instance the number of the instance which shall be solved, requiredDecrease a factor of required improvement <=1 in each iteration step, pcoCorrect a boolean telling if the heuristic shall consider the correct PCOs or shall also allow connections between legs of the same train
#solves the local search heuristics iteratively
def local_search(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin, timeLimit, instance, requiredDecrease, pcoCorrect):
	
	start_time = time.time()
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	intervalRange = 1
	
	#compute the intervals and value of the given current departure times
	maxVal, I = curMaximum.computeCurrentMaximum(instance, pcoCorrect)
	for index, m in enumerate(I):
		if m == maxVal:
			maxIndex = index
			break
	
	#get the legs that shall be fixed in the first iterating step
	fixedLegs, fixedTimes, variableLegs = setCurDepTimes(legList, maxIndex)
	
	#only needed if the first iterating step is infeasible or USR_OBJ_LIMIT is reached in the first step
	legDepartureTime = {}
	for j in legList:
		legDepartureTime[j['LegID']] = j['CurrentDepartureTime']
	
	elapsed_time = time.time() - start_time
	
	oldModel = None
	oldX = {}
	TLegs = {}
	#get the feasible departure times for each leg and store them in a dictionary
	for leg in legList:
		TLegs[leg['LegID']] = range(leg['EarliestDepartureTime'], leg['LatestDepartureTime'] + 1)
		for t in TLegs[leg['LegID']]:
			if t != leg['CurrentDepartureTime']:
				oldX[leg['LegID'], t] = 0
			else:
				oldX[leg['LegID'], t] = 1
	
	while elapsed_time < timeLimit:
		
		#only happens in the first iterating step and is only needed if all models are interrupted or infeasible or reach the timelimit
		if oldModel == None:
			legDepartureTime = {}
			for j in legList:
				legDepartureTime[j['LegID']] = j['CurrentDepartureTime']
		
		print("\nargMax: ", maxIndex)
		print("maxVal: ", maxVal)
		print("I: ", I)
		print("intervalRange: ", intervalRange)
		print("nrFixedLegs: ", len(fixedLegs))
		print("nrVarLegs: ", len(variableLegs))
		print("elapsed time:", elapsed_time, "s\n")
		prevMax = maxVal
		prevI = I
		
		elapsed_time = time.time() - start_time
		
		#solve the EETT model with fixed legs
		model, x, a, I, maxVal = solve_heuristic(trainDic, powerDic, fixedLegs, fixedTimes, T_m, TLegs, PL, ST, PassConOrd, timeHorizonMin, instance, maxVal, requiredDecrease, timeLimit - elapsed_time)
		
		
		if maxVal == 0:
			maxVal = prevMax
			x = oldX.copy()
		
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
				createSolution(maxVal, x, TLegs, legList, instance, requiredDecrease, "timelimit in model reached!", pcoCorrect)
			else:
				createSolution(maxVal, oldX, TLegs, legList, instance, requiredDecrease, "timelimit in model reached!", pcoCorrect)
			break
		
		#keyboard interrupt
		if model.status == 11:
			if len(I) > 0:
				createSolution(maxVal, x, TLegs, legList, instance, requiredDecrease, "keyboard interrupt; upper bound created as solution", pcoCorrect)
			else:
				createSolution(maxVal, oldX, TLegs, legList, instance, requiredDecrease, "keyboard interrupt; no upper bound found, old solution created", pcoCorrect)
			break
		
		oldModel = model
		oldX = x.copy()
		
		#get the new maximal index
		for index, m in enumerate(I):
			if m == maxVal:
				newMaxIndex = index
				break
		
		if newMaxIndex == maxIndex:
			if maxIndex - intervalRange <= 0 and maxIndex + intervalRange >= len(I):
				elapsed_time = time.time() - start_time
				createSolution(maxVal, x, TLegs, legList, instance, requiredDecrease, "optimal solution found! \n time: " + str(elapsed_time) + "s", pcoCorrect)
				break
			
			intervalRange += 1
		else:
			intervalRange = 1
		
		maxIndex = newMaxIndex
		
		legDepartureTime = {}
		
		#set the new departure times as the return of the EETT model
		for j_id, t in x:
			if x[j_id, t].X > 0.5:
				legDepartureTime[j_id] = t
		
		#get the new fixed legs
		fixedLegs, variableLegs = getFixedLegs(legList, legDepartureTime, fixedTimes, maxIndex, intervalRange)
		
		elapsed_time = time.time() - start_time
	
	if elapsed_time >= timeLimit:
		createSolution(maxVal, oldX, TLegs, legList, instance, requiredDecrease, "timelimit reached! elapsed time: " + str(elapsed_time) + "s", pcoCorrect)
	