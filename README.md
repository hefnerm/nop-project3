# nop-project3
code for the third project of the lecture nop from Lucia Ortjohann and Moritz Hefner

python version you need:
	python3.6

packages you need:
	gurobipy

scripts:
	scriptSolveEETTModel.py 				solves the EETT-Model for alle instances with timelimit 5h
	scriptSolveLocalSearchHeuristic.py 		with parameters
											pcoCorrect = True, requiredDecrease = 1 		runs the heuristik 1 
											pcoCorrect = True, requiredDecrease = 0.999		runs the heuristik 2
											pcoCorrect = False, requiredDecrease = 1		runs the heuristik described in chapter 4.4

    scriptSolveInstance1WithStartSolution.py 	runs the EETT-Model for instance 1 with the startsolution from chapter 4.4


other files:
	readWrite.py 				reads the data
	preprocess.py				mainly gets sets for the model plus new EDT and LDT
	curMaximum.py 				calculates for every intervall the average power consumption and gives also the highest intervall
	localSearchHeuristic.py 	solves the heuristics
	modelEETT.py 				gurobi model solves the EETT-model
	modelEETTStartSolution.py 	gurobi model sovles the EETT-model with a start solution
	solution_checker.py 		solution checker in python3.6 version

solution folders:
	solutionsModelEETT					solutions of the EETT-model with timelimit 5h, solution_everythin gives the bounds, gaps and time of 									 all instances
	solutions_greedy_heuristic			solutions of heuristic 1 5h
	solutions_greedy_heuristic_30min 	solutions of heuristic 1 30min
	solutions_greedy_heuristic_requriedDecrease 		solutions of heuristic 2 5h
	solutions_greedy_heuristic_requriedDecrease_30min   solutions of heuristic 2 30min
	solutions_greedy_heuristic_withError				soltuions of heuristic 4.4 