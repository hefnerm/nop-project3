from gurobipy import *
import math

def legHasPredec(trainDic, leg):
	
	for train in trainDic['Trains']:
		if leg == train['Legs'][1]:
			return True
	
	return False

def solve_EETT(trainDic, powerDic, T_m, PL, ST, PassConOrd, timeHorizonMin):
	
	legList = []
	for train in trainDic['Trains']:
		for leg in train['Legs']:
			legList.append(leg)
	
	maxLatestDepTime = 0
	maxTravelTime = 0
	for leg in legList:
		if leg['LatestDepartureTime'] > maxLatestDepTime:
			maxLatestDepTime = leg['LatestDepartureTime']
		if leg['TravelTime'] > maxTravelTime:
			maxTravelTime = leg['TravelTime']
	
	model = Model("Energy efficient train timetable problem")
	
	
	
	#variables
	
	x = {}
	for j in legList:
		for t in T_m: #range(0, maxLatestDepTime + maxTravelTime + 1): ######################################################################original: T_m
			x[j['LegID'], t] = model.addVar(vtype=GRB.BINARY, name="x_" + str(j['LegID']) + "_" + str(t))
	
	a = {}
	for tau_m in T_m:
		for tau in range(60*tau_m, 60*tau_m + 60):###############################################################CHECK THIS RANGE
			a[tau] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="a_" + str(tau))
	
	I = {}
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		I[i] = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name="I_" + str(i))
	
	av = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, obj=1.0, name="average")
	
	model.update()
	
	#constraints
	
	#(1)
	for i in legList:
		model.addConstr(i['EarliestDepartureTime'] <= quicksum(t*x[i['LegID'], t] for t in T_m))
		model.addConstr(quicksum(t*x[i['LegID'], t] for t in T_m) <= i['LatestDepartureTime'])
	
	#(2)
	for j in legList:
		if legHasPredec(trainDic, j):
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
			#print("\ntau: ", tau)
			#for j in legSet:
				#for t in range(max(tau_m - j['TravelTime'], j['EarliestDepartureTime']), tau_m + 1):
					#print("len powerDic: ", len(powerDic[j['LegID']]))
					#print(powerDic[j['LegID']])
					#print("tau_m: ", tau_m)
					#print("t: ", t, " tau - t*60: ", tau-t*60)
					#print("j: ", j)
					#print(powerDic[j['LegID']][tau - t*60])
			if tau - 60*tau_m > 0:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'] + 1, j['EarliestDepartureTime']), tau_m + 1)) for j in legSet))
			else:
				model.addConstr(a[tau] >= quicksum(quicksum(x[j['LegID'], t] * powerDic[j['LegID']][tau - t*60] for t in range(max(tau_m - j['TravelTime'], j['EarliestDepartureTime']), tau_m + 1)) for j in legSet))
			###########################################################CHECK POWER ACCESS
	
	#(7)
	for i in range(1, math.floor(timeHorizonMin/15) + 1):
		model.addConstr(I[i] == (quicksum(a[tau] for tau in range(15*(i-1)*60 + 1, 15*i*60 - 1 + 1)) + a[15*(i-1)*60]/2 + a[15*i*60]/2 )/900)
	
	if math.floor(timeHorizonMin/15) != timeHorizonMin/15:
		intervalLength = (timeHorizonMin - math.floor(timeHorizonMin/15)*15)*60
		#print(a[15*math.floor(timeHorizonMin/15)*60]/2 + a[15*math.floor(timeHorizonMin/15)*60 + intervalLength]/2)
		
		model.addConstr(I[math.ceil(timeHorizonMin/15)] == (quicksum(a[tau] for tau in range(15*math.floor(timeHorizonMin/15)*60 + 1, 15*math.floor(timeHorizonMin/15)*60 + intervalLength)) + a[15*math.floor(timeHorizonMin/15)*60]/2 + a[15*math.floor(timeHorizonMin/15)*60 + intervalLength]/2)/intervalLength)
	
	#(8)
	for i in range(1, math.ceil(timeHorizonMin/15) + 1):
		model.addConstr(av >= I[i])
	
	model.optimize()
	
	return model, x, I, av
	