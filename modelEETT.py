from gurobipy import *
import json
import math

#input: trainDic: a dictionary containing all train information in the format of the return of readInstance readWrite.py and a leg
#output: true, if the leg is the starting leg of a train (the leg has no prior leg) or false otherwise
def legHasNoPredec(trainDic, leg):
	
	for train in trainDic['Trains']:
		if leg == train['Legs'][0]:
			return True
	
	return False

def solve_EETT(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin):
	
	#create a list of all legs
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	model = Model("Energy efficient train timetable problem")
	
	model.Params.SOLUTION_LIMIT = 1
	
	#variables
	
	x = {}
	#x[j, t] = 1 if the leg j departs at minute t, 0 otherwise
	for j in legList:
		for t in T_m:
			x[j['LegID'], t] = model.addVar(vtype=GRB.BINARY, name="x_" + str(j['LegID']) + "_" + str(t))
	
	a = {}
	#a[tau] is the nonnegative poweramount of the whole system at second tau
	for tau_m in T_m:
		for tau in range(60*tau_m, 60*tau_m + 60):###############################################################CHECK THIS RANGE
			a[tau] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="a_" + str(tau))
	
	I = {}
	#I[i] is the average powerconsumption in the i'st interval
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		I[i] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="I_" + str(i))
	
	#maximum forms the value of the maximal interval
	maximum = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=1.0, name="maximum")
	
	model.update()
	
	#constraints
	
	#(1)
	for i in legList:
		model.addConstr(i['EarliestDepartureTime'] <= quicksum(t*x[i['LegID'], t] for t in T_m))
		model.addConstr(quicksum(t*x[i['LegID'], t] for t in T_m) <= i['LatestDepartureTime'])
	
	#(2)
	for j in legList:
		if not legHasNoPredec(trainDic, j):
			i = PL[j['LegID']]
			model.addConstr(quicksum(t*x[i['LegID'], t] for t in T_m) + i['TravelTime'] + i['MinimumStoppingTime'] <= quicksum(t*x[j['LegID'], t] for t in T_m))
	
	#(3)
	for j in legList:
		if not ST[j['LegID']] == False:
			i = ST[j['LegID']]
			model.addConstr(quicksum(t*x[j['LegID'], t] for t in T_m) + j['MinimumHeadwayTime'] <= quicksum(t*x[i['LegID'], t] for t in T_m))
	
	#(4)
	for [i, j] in PassConOrd:
		model.addConstr(5 <= -(quicksum(t*x[i['LegID'], t] for t in T_m) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in T_m))
		model.addConstr(-(quicksum(t*x[i['LegID'], t] for t in T_m) + i['TravelTime']) + quicksum(t*x[j['LegID'], t] for t in T_m) <= 15)
	
	#(5)
	for j in legList:
		model.addConstr(quicksum(x[j['LegID'], t] for t in T_m) == 1)
	
	#(6)
	for tau_m in T_m:
		#print("tau_m: ", tau_m)
		legSet = []
		for leg in legList:
			if leg['EarliestDepartureTime'] <= tau_m <= leg['LatestDepartureTime'] + leg['TravelTime']:
				legSet.append(leg)
		
		for tau in range(60*tau_m, 60*tau_m + 60):###############################CHECK THIS RANGE LIKE ABOVE
			if tau - 60*tau_m > 0:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'] + 1, j['EarliestDepartureTime']), tau_m + 1)) for j in legSet))
			else:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'], j['EarliestDepartureTime']), tau_m + 1)) for j in legSet))
			###########################################################CHECK POWER ACCESS
	
	#(7)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(I[i] == (quicksum(a[tau] for tau in range(15*(i-1)*60 + 1, min(15*i*60 - 1 + 1, timeHorizonMin*60))) + a[15*(i-1)*60]/2 + a[min(15*i*60, timeHorizonMin*60 + 1)]/2 )/900)
	
	
	#(8)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(maximum >= I[i])
	
	model.optimize()
	
	if model.status in [2, 9, 10, 11]:
		solution = { "Legs": {}}
		for j in legList:
			for t in T_m:
				if x[j['LegID'], t].X > 0.5:
					(solution["Legs"])[j['LegID']] = t
		
		with open('solution.json.txt', 'w', encoding='utf-8') as outfile:
			json.dump(solution, outfile)
	
	return model, x, I, maximum
	