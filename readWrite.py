import json
import codecs

def readInstance(number):
	if not number in range(1, 11):
		print("argument to read instance must be a number between 1 and 10")
		exit()
	
	with codecs.open("./instances/instance_data_" + str(number) + ".json.txt", "r", encoding="utf-8") as infile:
		data = json.load(infile, encoding="utf-8")
	
	trainDic = {'Trains': data['Trains']}
	
	with codecs.open("./instances/power_data_" + str(number) + ".json.txt", "r", encoding="utf-8") as infile:
		data = json.load(infile, encoding="utf-8")
	
	powerDic = {'Powerprofiles': data['Powerprofiles']}
	
	return trainDic, powerDic