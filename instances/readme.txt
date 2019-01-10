# README:  
# This file gives an overview over the whole data folder

*** Statistics:
Instance Trains Legs
1        13     206
2        26     241
3        37     352
4        48     676
5        71     863
6        73     712
7        126    1524
8        182    3709
9        237    1808
10       277    2641

*** File format:
* The structure of the files is described below.
* The files are given in JSON-Format
  (see http://en.wikipedia.org/wiki/JSON)
* Note that in JSON, the order of attributes is not specified
* The files can be read with any JSON-library
* In Python 2.7 for example:

import json
import codecs

with codecs.open("instance_data_1.json.txt", "r", encoding="utf-8") as infile:
    data = json.load(infile, encoding="utf-8")


*** General notes on the instances:
* Each instance consists of two files:
* instance_data contains the timetable information
* power_data contains the power profiles for each leg.
* Two files with the same number form one instance.

*** Description of instance_data:
* TrainID uniquely identifies each train. (Integer)
* TrackID uniquely identifies each track. (Integer)
* LegID uniquely identifies each train run on a given track. (Integer)
* StartStationID: uniquely identifies the origin of the leg. (Integer)
* EndStationID: uniquely identifies the destination of the leg. (Integer)
* EarliestDepatureTime describes the earliest departure time of the leg. (Integer)
* LatestDepatureTime describes the latest departure time of the leg. (Integer)
* CurrentDepatureTime describes the departure time in the current time table. (Integer)
* TravelTime describes the time the train runs to the next station in minutes. (Integer)
* MinimumStoppingTime describes the minimum time the trains needs to stay in the following station (if one exists) in minutes. (Integer)
* MinimumHeadwayTime describes the minimum time the next train on the same route has to wait until it can depart. (Integer)

*** Comments on instance_data
* The trains can only depart every full minute from the EarliestDepatureTime until LatestDepatureTime.
* Two consecutive trains using the same track have to
  satisfy a safety constraint. The departure of the later train must greater or equal to
  the departureTime of the earlier train plus the minimum headway time specified for the earlier train.
* This constraint implicitly enforces the same order of the trains on each track as established in the orginal timetable.
  That means the order of the trains is fixed and is not part of the optimization.
* At each station, the new timetable has to respect the passenger connections established in the original timetable.
  If the arrival of one train at a given station and the departure of another train take place within an interval of 5 to 15 minutes in the old timetable,
  this relation has to be preserved in the new timetable.

*** Example for instance_data:
{
  "Trains": [
  {
    "TrainID": 1,
    "Legs": [
      {
        "StartStationID": 1, 
        "LatestDepartureTime": 4, 
        "CurrentDepartureTime": 1, 
        "EndStationID": 2, 
        "MinimumHeadwayTime": 2, 
        "TrackID": 1, 
        "EarliestDepartureTime": 0, 
        "MinimumStoppingTime": 1, 
        "TravelTime": 3, 
        "LegID": 1
      },
      {
        ...
        "LegID": 2
      }
    ]
  },
  {
    "TrainID": 2,
    ...
  }
  ]
}

*** Structure of power_data:
* LegID correspond to the same LegID as in the instance_file and is unique. (Integer)
* Powerprofile contains exactly TravelTime*60+1 time steps (seconds), where the power is measured (in MW). (Float)

*** Example for power_data:
{
  "Powerprofiles": [
    {
      "LegID": 1, 
      "Powerprofile": [
        0.0, 
        0.031,
	...
        ]
    },
    {
      "LegID": 2, 
      "Powerprofile": [
        0.0, 
        0.02,
	... 
        ]
    }
}

