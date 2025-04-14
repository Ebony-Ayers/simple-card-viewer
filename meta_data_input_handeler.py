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
		self.rarity = None
	
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
			 self.abilities,
			 self.rarity,)
		return str(t)
	
	def fromStr(self, s):
		t = ast.literal_eval(s)
		#if there are any new properties added that aren't currently in the DB create blank enteries
		t += tuple([None] * (13 - len(t)))
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
		self.rarity = t[12]
	
	def mergeWith(self, r):
		if r.cardType != None:
			self.cardType = r.cardType
		if r.subType != None:
			self.subType = r.subType
		if r.legendary != None:
			self.legendary = r.legendary
		if r.trueCmc != None:
			self.trueCmc = r.trueCmc
		if r.lowestCmc != None:
			self.lowestCmc = r.lowestCmc
		if r.onCurve != None:
			self.onCurve = r.onCurve
		if r.maximumColor != None:
			self.maximumColor = r.maximumColor
		if r.minimumColors != None:
			self.minimumColors = r.minimumColors
		if r.power != None:
			self.power = r.power
		if r.toughness != None:
			self.toughness = r.toughness
		if r.keywords != None:
			self.keywords = r.keywords
		if r.abilities != None:
			self.abilities = r.abilities
		if r.rarity != None:
			self.rarity = r.rarity


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
			

def createRecord(propertiesToModify):
	record = Record()
	
	#super type
	if "cardType" in propertiesToModify:
		record.cardType = validateSingleInputEnum("Enter the card type", False, enums.shortTypes, enums.longTypes)
	#subtypes
	if "subType" in propertiesToModify:
		if not ((record.cardType & enums.longTypes["instant"]) or (record.cardType & enums.longTypes["sorcery"]) or (record.cardType & enums.longTypes["planeswalker"])):
			record.subType = list(map(lambda s : s.lower().strip(), input("Enter the card subtypes: ").split(" ")))
			if record.subType == ['']:
				record.subType = None
		else:
			record.subType = None
	#legendary
	if "legendary" in propertiesToModify:
		if not ((record.cardType & enums.longTypes["instant"]) or (record.cardType & enums.longTypes["sorcery"]) or (record.cardType & enums.longTypes["planeswalker"])):
			record.legendary = validateBool("Is this card legendary")
		else:
			record.legendary = False
	#cmc
	if "cmc" in propertiesToModify:
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
	if "onCurve" in propertiesToModify:
		if not (record.cardType & enums.longTypes["land"]):
			record.onCurve = validateBool("Is this card on curve")
		else:
			record.onCurve = True
	#maximum color
	if "color" in propertiesToModify: 
		record.maximumColor = validateMultiInputEnum("Enter the maximum color", False, enums.shortColors, enums.longColors)
	#minimum colors
		if validateBool("Enter minimum colors (y/n)"):
			if not (record.cardType & enums.longTypes["land"]):
				record.minimumColors = []
				while True:
					minColor = validateMultiInputEnum("Enter a minimum color", False, enums.shortColors, enums.longColors)
					#a and not b returns the bits in a that are not in b
					#the minimum color must be a subset of the max color or be colorless
					if (minColor & (~record.maximumColor)) and (minColor != enums.longColors["colorless"]):
						print("\nInvalid input. The minimum color cannot be greater than the maximum color. Please try again.\n")
						continue
					record.minimumColors.append(minColor)
					if not validateBool("Add another minimim color (y/n)"):
						break
				if record.maximumColor not in record.minimumColors:
					record.minimumColors.append(record.maximumColor)
			else:
				record.minimumColors = None
		else:
			record.minimumColors = [record.maximumColor]
	#p/t
	if "p/t" in propertiesToModify:
		if record.cardType & enums.longTypes["creature"] or (record.subType != None and "vehicle" in record.subType):
			record.power = validateInt("Enter the power")
			record.toughness = validateInt("Enter the toughness")
		else:
			record.power = None
			record.toughness = None
	#keywords
	if "keywords" in propertiesToModify:
		if record.cardType & enums.longTypes["creature"] or (record.subType != None and "vehicle" in record.subType):
			record.keywords = validateMultiInputEnum("Enter the card keywords", True, enums.shortKeywords, enums.longKeywords)
		else:
			record.keywords = None
	#abilities
	if "abilities" in propertiesToModify:
		record.abilities = validateMultiInputEnum("Enter the card abilities", True, enums.longAbilities)
	#rarity
	if "rarity" in propertiesToModify:
		record.rarity = validateSingleInputEnum("Enter the card rarity", False, enums.shortRarities, enums.longRarities)
	
	return record
	
#metadata is a disctionary of records keyed by card name
def createMetaData(metaData, cardName, shouldSkipExistingCards, shouldMofigyExistingCards, modifySingleCard, propertiesToModify):
	print()
	shouldSkip = False
	#check if the card is already in the DB
	if cardName in metaData.keys():
		#check if command line arguments specify skipping behavior
		#if no skipping behavior is specified both skip existing and modify existing will be false
		if shouldSkipExistingCards or shouldMofigyExistingCards:
			shouldSkip = shouldSkipExistingCards or not shouldMofigyExistingCards
		elif modifySingleCard:
			shouldSkip = False
		#fall back to asking user
		else:
			shouldSkip = validateBool(f"\"{cardName}\" appears in the data base. would you like to skip (y/n)")
	if (cardName == "") or shouldSkip:
		return
	else:
		newRecord = createRecord(propertiesToModify)
		oldRecord = metaData.get(cardName, Record())
		oldRecord.mergeWith(newRecord)
		metaData[cardName] = oldRecord

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
	print("rarity =", record.rarity)
