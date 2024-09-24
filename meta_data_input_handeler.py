import enums
import ast

class Record:
	def __init__(self):
		self.cardType = None
		self.subType = None
		self.legendary = None
		self.trueCmc = None
		self.lowestCmc = None
		self.onCurve = None
		self.maximumColor = None
		self.minimumColors = None
		self.power = None
		self.toughness = None
		self.keywords = None
		self.abilities = None
	
	def toStr(self):
		t = (self.cardType,
			 self.subType,
			 self.legendary,
			 self.trueCmc,
			 self.lowestCmc,
			 self.onCurve,
			 self.maximumColor,
			 self.minimumColors,
			 self.power,
			 self.toughness,
			 self.keywords,
			 self.abilities,)
		return str(t)
	
	def fromStr(self, s):
		t = ast.literal_eval(s)
		self.cardType = t[0]
		self.subType = t[1]
		self.legendary = t[2]
		self.trueCmc = t[3]
		self.lowestCmc = t[4]
		self.onCurve = t[5]
		self.maximumColor = t[6]
		self.minimumColors = t[7]
		self.power = t[8]
		self.toughness = t[9]
		self.keywords = t[10]
		self.abilities = t[11]


def validateInt(message):
	while True:
		userInput = input(message + ": ").strip()
		if userInput.isnumeric():
			return int(userInput)
		else:
			print("\nInvalid input. Input must be an integer. Please try again.\n")

def validateBool(message):
	while True:
		userInput = input(message + ": ").lower().strip()
		if userInput in ("true", "yes", "y"):
			return True
		elif userInput in ("false", "no", "n"):
			return False
		else:
			print("\nInvalid input. Input must be an integer. Please try again.\n")

def validateSingleInputEnum(message, allowNoInput, *args):
	while True:
		userInput = input(message + ": ").strip().lower()
		if allowNoInput:
			if userInput == "":
				return None
		for arg in args:
			if userInput in arg:
				return arg[userInput]
		print("\nInvalid input. Input did not match any of the options. Please try again.\n")

def validateMultiInputEnum(message, allowNoInput, *args):
	while True:
		returnValue = 0
		userInputs = input(message + ": ").strip().lower().split(" ")
		if allowNoInput:
			if userInputs == [""]:
				return None
		foundAllInputs = True
		for userInput in userInputs:
			userInput = userInput.strip()
			#check a given input again all the opions. In the event that the input is found keep going otherwise break to the outmost loop
			foundInput = False
			for arg in args:
				if userInput in arg:
					#as we are dealing with bitsets we or the answer into the result
					returnValue |= arg[userInput]
					foundInput = True
					break
			if not foundInput:
				print(f"\nInvalid input. Input {userInput} did not match any of the options. Please try again.\n")
				foundAllInputs = False
				break
		#only when all inputs have been validated can we leave the outer loop
		if foundAllInputs:
			return returnValue
			

def createRecord():
	record = Record()
	
	#super type
	record.cardType = validateSingleInputEnum("Enter the card type", False, enums.shortTypes, enums.longTypes)
	#subtypes
	record.subType = list(map(lambda s : s.lower().strip(), input("Enter the card subtypes: ").split(" ")))
	#legendary
	record.legendary = validateBool("Is this card legendary")
	#cmc
	while True:
		if not (record.cardType & enums.longTypes["land"]):
			record.trueCmc = validateInt("Enter the true CMC")
			record.lowestCmc = validateInt("Enter the lowest CMC")
		else:
			record.trueCmc = 0
			record.lowestCmc = 0
			
		if record.lowestCmc > record.trueCmc:
			print("\nInvalid input. Lowest CMC cannot be less than true CMC. Please try again.\n")
		else:
			break
	#curve
	record.onCurve = validateBool("Is this card on curve")
	#maximum color
	record.maximumColor = validateMultiInputEnum("Enter the maximum color", False, enums.shortColors, enums.longColors)
	#minimum colors
	if not (record.cardType & enums.longTypes["land"]):
		record.minimumColors = []
		while True:
			minColor = validateMultiInputEnum("Enter a minimum color", False, enums.shortColors, enums.longColors)
			#a and not b returns the bits in a that are not in b
			#the minimum color must be a subset of the max color
			if minColor & (~record.maximumColor):
				print("\nInvalid input. The minimum color cannot be greater than the maximum color. Please try again.\n")
				continue
			record.minimumColors.append(minColor)
			if not validateBool("Add another minimim color (y/n)"):
				break
		if record.maximumColor not in record.minimumColors:
			record.minimumColors.append(record.maximumColor)
	else:
		record.minimumColors = None
	#p/t
	if record.cardType & enums.longTypes["creature"]:
		record.power = validateInt("Enter the power")
		record.toughness = validateInt("Enter the toughness")
	else:
		record.power = None
		record.toughness = None
	#keywords
	if record.cardType & enums.longTypes["creature"]:
		record.keywords = validateMultiInputEnum("Enter the card keywords", True, enums.shortKeywords, enums.longKeywords)
	else:
		record.keywords = None
	#abilities
	record.abilities = validateMultiInputEnum("Enter the card abilities", True, enums.longAbilities)
	
	return record
	
#metadata is a disctionary of records keyed by card name
def createMetaData(metaData):
	print()
	cardName = input("Enter the current cards name of blank to skip: ").strip()
	shouldSkip = False
	if cardName in metaData.keys():
		shouldSkip = validateBool(f"\"{cardName}\" appears in the data base. would you like to skip")
	if (cardName == "") or shouldSkip:
		return
	else:
		record = createRecord()
		metaData[cardName] = record

def serialiseMetaData(metaData, fileName):
	with open(fileName, 'w') as f:
		for key,value in metaData.items():
			f.write(key + ":" + value.toStr() + "\n")

def deserialiseMetaData(metaData, fileName):
	with open(fileName, 'r') as f:
		for line in f:
			l = line.split(":")
			record = Record()
			record.fromStr(l[1])
			metaData[l[0]] = record
	
if __name__ == "__main__":
	print("You aren't supposed to run this file.")
	print("Testing createRecord()")
	
	record = createRecord()
	print("cardType =", record.cardType)
	print("subType =", record.subType)
	print("legendary =", record.legendary)
	print("trueCmc =", record.trueCmc)
	print("lowestCmc =", record.lowestCmc)
	print("onCurve =", record.onCurve)
	print("maximumColor =", record.maximumColor)
	print("minimumColors =", record.minimumColors)
	print("power =", record.power)
	print("toughness =", record.toughness)
	print("keywords =", record.keywords)
	print("abilities =", record.abilities)