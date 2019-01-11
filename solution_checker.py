"""

Open Research Challenge FAU 2015

Solution Checker

Tested under Python 2.7

Call script:

python solution_checker.py <path_to_instance_file> <path_to_power_file> <path_to_solution_file>

"""

from __future__ import division



import sys

import math

import numpy

import collections

import json

import codecs





class TrainModel:



	route_ordered_trains = collections.defaultdict(list)

	routes = dict()

	train_station_ordered_departure_trains = collections.defaultdict(list)



	def __init__(cls, scheduling_interval, number_of_trains, trains, max_power):

		cls.scheduling_interval = scheduling_interval

		cls.number_of_trains = number_of_trains

		cls.trains = trains

		cls.max_power = max_power





class Train:



	def __init__( cls, train_number, legs):

		cls.train_number = train_number

		cls.legs = legs





class Leg:



	departure_time_in_solution = -1
	train_number = -1



	def __init__(cls, route, travel_time, dwell_time_at_endstation, earliest_departure_time, latest_departure_time,

			current_departure_time, position_on_route, safety_distance_for_next_train, power_profile, leg_id):

		cls.route = route

		cls.travel_time = travel_time

		cls.dwell_time_at_endstation = dwell_time_at_endstation

		cls.earliest_departure_time = earliest_departure_time

		cls.latest_departure_time = latest_departure_time

		cls.current_departure_time = current_departure_time

		cls.position_on_route = position_on_route

		cls.safety_distance_for_next_train = safety_distance_for_next_train

		cls.power_profile = power_profile

		cls.leg_id = leg_id





class Route:



	def __init__(cls, route_number, departure_station, destination_station):

		cls.route_number = route_number

		cls.departure_station = departure_station

		cls.destination_station = destination_station





def return_position(Leg):

	return Leg.position_on_route





def return_depart_time(Leg):

	return Leg.current_departure_time



try:

	path_to_instance_file = sys.argv[1]

	path_to_power_file = sys.argv[2]

	path_to_solution_file = sys.argv[3]

except:

	print ("Call script with: python solution_checker.py <path_to_instance_file> <path_to_power_file> <path_to_solution_file>")

	exit()





try:

	with codecs.open(path_to_instance_file, 'r') as infile:

		inst_data = json.load(infile, encoding="utf-8")

	with codecs.open(path_to_power_file, 'r') as infile:

		power_data = json.load(infile, encoding="utf-8")

	with codecs.open(path_to_solution_file, 'r') as infile:

		solution_data = json.load(infile, encoding="utf-8")

except:

	print ("Files could not be opened correctly")

	exit()



# Type checking

for k in solution_data["Legs"]:

	if isinstance(solution_data["Legs"][k], ( int, int ) ) == False:

		print ("Solution departure time is not of type integer, legid =", k, ",departure time =", solution_data["Legs"][k])

		print ("Please make sure the departure time is no float number or string")

		exit()



try:

	power = {}

	for pp in power_data["Powerprofiles"]:

		power[pp["LegID"]] = numpy.array(pp["Powerprofile"])

	model = TrainModel(0, 0,[], 0)

	model.scheduling_interval = 0

	model.number_of_trains = len(inst_data[u"Trains"])

	for ztrain in inst_data[u"Trains"]:

		train = Train(ztrain[u"TrainID"], [])

		for zleg in ztrain[u"Legs"]:
	  
			position_on_route = -1

			if zleg["TrackID"] not in model.routes:

				model.routes[zleg["TrackID"]] = (Route(zleg["TrackID"],zleg["StartStationID"],zleg["EndStationID"]))

			leg = Leg(model.routes[zleg["TrackID"]], zleg["TravelTime"], zleg["MinimumStoppingTime"], zleg["EarliestDepartureTime"],

					zleg["LatestDepartureTime"], zleg["CurrentDepartureTime"], position_on_route, zleg["MinimumHeadwayTime"],

					power[zleg["LegID"]],zleg["LegID"])

			leg.departure_time_in_solution = solution_data["Legs"]["{}".format(zleg["LegID"])]
            
			leg.train_number= ztrain[u"TrainID"]

			endtime = zleg["LatestDepartureTime"] + zleg["TravelTime"]

			if endtime > model.scheduling_interval:

				model.scheduling_interval = endtime

			model.route_ordered_trains[zleg["TrackID"]].append(leg)

			model.train_station_ordered_departure_trains[model.routes[zleg["TrackID"]].departure_station].append(leg)

			train.legs.append(leg)

		model.trains.append(train)

	for nr in model.route_ordered_trains.keys():

		model.route_ordered_trains[nr] = sorted(model.route_ordered_trains[nr], key = return_depart_time)

	for nr in model.train_station_ordered_departure_trains.keys():

		model.train_station_ordered_departure_trains[nr] = sorted(model.train_station_ordered_departure_trains[nr], key = return_depart_time)

except:

	print ("Files could not be parsed correctly. Files are corrupt or do not belong together.")

	exit()



try:

	# Departure Time Feasibility Test

	for t in range(len(model.trains)):

		for r in range(len(model.trains[t].legs)):

			current_train = model.trains[t].legs[r]

			if current_train.departure_time_in_solution < current_train.earliest_departure_time or current_train.departure_time_in_solution > current_train.latest_departure_time:

				print ("leg {} violates feasible departure time".format(current_train.leg_id))

				exit()



	# Minimum Stopping Time Test

	for t in range(len(model.trains)):

		for r in range(len(model.trains[t].legs)):

			current_train = model.trains[t].legs[r]

			if r != len(model.trains[t].legs)-1:

				nextTrain = model.trains[t].legs[r+1]

				if nextTrain.departure_time_in_solution < current_train.departure_time_in_solution + current_train.travel_time + current_train.dwell_time_at_endstation:

					print ("leg {} and leg {} violates the minimum stopping time".format(current_train.leg_id, nextTrain.leg_id))

					exit()



	# Safety distance Test

	for nr in model.route_ordered_trains.keys():

		for p in range(len(model.route_ordered_trains[nr])):

			current_train = model.route_ordered_trains[nr][p]

			if current_train.safety_distance_for_next_train == 0:

				continue

			if p != len(model.route_ordered_trains[nr])-1:

				nextTrain = model.route_ordered_trains[nr][p+1]

				if nextTrain.departure_time_in_solution < current_train.departure_time_in_solution + current_train.safety_distance_for_next_train:

					print ("leg {} and leg {} violates the minimum headway distance".format(current_train.leg_id, nextTrain.leg_id))

					exit()

                    

	# Connection Test

	for t in range(len(model.trains)):

		for r in range(len(model.trains[t].legs)):

			current_train = model.trains[t].legs[r]

			EndBahnhof = current_train.route.destination_station

			endtime = current_train.current_departure_time+current_train.travel_time

			for p in range(len(model.train_station_ordered_departure_trains[EndBahnhof])):

				# If legs belong to the same train we skip connection test

				if model.trains[t].train_number == model.train_station_ordered_departure_trains[EndBahnhof][p].train_number:
		    
					continue
		  
				abfahrt = model.train_station_ordered_departure_trains[EndBahnhof][p].current_departure_time

				zeitspanne = abfahrt - endtime

				if zeitspanne >= 5 and zeitspanne <= 15:

					nextTrain = model.train_station_ordered_departure_trains[EndBahnhof][p]

					zeitspanne_neu = nextTrain.departure_time_in_solution - current_train.departure_time_in_solution - current_train.travel_time

					if zeitspanne_neu < 5 or zeitspanne_neu > 15:

						print ("leg {} and leg {} violates the interchange constraint".format(current_train.leg_id, nextTrain.leg_id))

						exit()

except:

	print ("Error while testing.")

	exit()

try:

	powerdemand = numpy.zeros(model.scheduling_interval*60+1)

	for t in range(len(model.trains)):

		for r in range(len(model.trains[t].legs)):

			current_train = model.trains[t].legs[r]

			dimstart = (current_train.departure_time_in_solution)*60

			dimend = (current_train.departure_time_in_solution+current_train.travel_time)*60+1

			powerdemand[dimstart:dimend] = powerdemand[dimstart:dimend] + current_train.power_profile



	number_of_middle_intervals = int(math.ceil((model.scheduling_interval*60+1)/float(901)))

	sum_middle_interval = []



	for t in range(number_of_middle_intervals):

		x_min = int(min((901-1)*(t+1), len(powerdemand)-1))

		sum_current_interval = sum(a for a in powerdemand[(901-1)*t+1:x_min] if a > 0)

		sum_current_interval += max(0.5 * powerdemand[(901-1)*t], 0)

		sum_current_interval += max(0.5 * powerdemand[x_min], 0)

		sum_middle_interval.append(sum_current_interval)



	middle_maxpeak = numpy.amax(sum_middle_interval)/float(900)

except:

	print ("Error while calculating objective. Files seems to be corrupt")

	exit()

for i in range(len(sum_middle_interval)):
	sum_middle_interval[i] = sum_middle_interval[i]/float(900)

print(sum_middle_interval)

print ("Solution is feasible with objective {}".format(middle_maxpeak))





