from gurobipy import *

model = Model("testModel")

model.Params.BestBdStop = 1

model.modelSense = GRB.MINIMIZE

t = model.addVar(vtype=GRB.CONTINUOUS, obj=1.0, name="t")

model.update()

model.addConstr(t >= 2)

model.optimize()

print(model.status)

print(model.ObjVal)
