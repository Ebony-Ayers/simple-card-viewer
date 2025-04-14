import pyglet
import os

import enums
from meta_data_input_handeler import Record

class Card:
	def __init__(self, name, image, data):
		self.name = name
		self.image = image
		self.data = data

CARD_WIDTH = 260
CARD_HEIGHT = 364
MARGIN = 10
#units are pixles per frame
SCROLL_SPEED = 15

DATA_BASE_FILE_NAME = "cardDB.txt"
CARDS_FOLDER_NAME = "cards/"

#global variables make pyglet much easier to use
numCardsTotal = 0
numCardsFiltered = 0
cardPositions = []
fullCardList = []
filteredCardList = []
metaData = {}
#enum:
#0 - grid
viewMode = 0
selectedCard = None
windowSize = (1280, 720)
numCardsPerRow = 0
#how many pixles to shift images as a result of scrolling
scrollOffset = 0

sortMode = "name"
POSSIBLE_SORT_MODES = ["name", "cmc", "lcmc", "tcmc", "color", "power", "toughness", "rarity"]

DEFULAT_RECORD = Record()
DEFULAT_RECORD.type = enums.longTypes["unknown"]
DEFULAT_RECORD.subType = None
DEFULAT_RECORD.legendary = False
DEFULAT_RECORD.trueCmc = 999999
DEFULAT_RECORD.lowestCmc = 999999
DEFULAT_RECORD.onCurve = True
DEFULAT_RECORD.maximumColor = enums.longColors["unknown"]
DEFULAT_RECORD.minimumColors = [enums.longColors["unknown"]]
DEFULAT_RECORD.power = False
DEFULAT_RECORD.toughness = False
DEFULAT_RECORD.keywords = []
DEFULAT_RECORD.abilities = []

def loadMetaData():
	global metaData
	
	with open(DATA_BASE_FILE_NAME, 'r') as f:
		for line in f:
			line = line.split(":")
			name = line[0]
			record = Record()
			record.fromStr(line[1])
			metaData[name] = record

#cache the images for each of the cards
def loadCards():
	global numCardsTotal, fullCardList, metaData
	
	cardsFolder = os.path.join(os.getcwd(), CARDS_FOLDER_NAME)
	for i,f in enumerate(os.listdir(cardsFolder)):
		if os.path.isfile(os.path.join(cardsFolder, f)):
			#read the image file in
			image = pyglet.resource.image(os.path.join(CARDS_FOLDER_NAME, f))
			#reduce the size to be reasonable
			image.width = CARD_WIDTH
			image.height = CARD_HEIGHT
			
			name = str(f)
			data = metaData.get(name, DEFULAT_RECORD)
			fullCardList.append(Card(name, image, data))
			numCardsTotal += 1

#filter then sort the cards based on the search criteria 
def filterSortCards():
	global fullCardList, filteredCardList, numCardsTotal, numCardsFiltered, sortMode

	filteredCardList = fullCardList.copy()
	numCardsFiltered = numCardsTotal
	
	if sortMode == "name":
		filteredCardList.sort(key = lambda x : x.name)
	elif sortMode == "cmc" or sortMode == "lcmc":
		filteredCardList.sort(key = lambda x : x.data.lowestCmc)
	elif sortMode == "tcmc":
		filteredCardList.sort(key = lambda x : x.data.trueCmc)
	elif sortMode == "color":
		print(filteredCardList[0].data.maximumColor)
		#colorless is the "last" color so by multiplying the number of bits which represents the number of colors with the "last" color will put all 2 color cards after single color cards and so on
		filteredCardList.sort(key = lambda x : x.data.maximumColor + (int.bit_count(x.data.maximumColor) * enums.longColors["colorless"]))
	elif sortMode == "power":
		filteredCardList.sort(key = lambda x : x.data.power if x.data.power != None else 999999)
	elif sortMode == "toughness":
		filteredCardList.sort(key = lambda x : x.data.toughness if x.data.toughness != None else 999999)
	elif sortMode == "rarity":
		filteredCardList.sort(key = lambda x : x.data.rarity)

#creeate a list of positions for the cards. The position stored is the bottom left corner.
def setPositions():
	global numCardsTotal, cardPositions, windowSize, numCardsPerRow
	cardPositions = [None] * numCardsTotal
	x = 0
	y = 0
	numCardsPerRow = (windowSize[0] - MARGIN) // (CARD_WIDTH + MARGIN)
	for i in range(numCardsTotal):
		cardPositions[i] = ((x * (CARD_WIDTH + MARGIN)) + MARGIN, windowSize[1] - ((y+1) * (CARD_HEIGHT + MARGIN)) - scrollOffset)
		x += 1
		if x >= numCardsPerRow:
			x = 0
			y += 1
	
#pyglet boiler plate
def initialisePyglet():
	window = pyglet.window.Window(1280, 720, "Simple Card Viewer")
	window.set_minimum_size(640,480)
	window.set_maximum_size(3840,2160)
	window.maximize()
	@window.event
	def on_draw():
		window.clear()
		drawFunc()
	@window.event
	def on_key_press(symbol, modifiers):
		keyboardPressHandeler(symbol, modifiers)
	@window.event
	def on_key_release(symbol, modifiers):
		keyboardReleaseHandeler(symbol,modifiers)
	@window.event
	def on_mouse_press(x, y, button, modifiers):
		mousePressHandeler(x, y, button, modifiers)
	@window.event
	def on_mouse_release(x, y, button, modifiers):
		mouseReleaseHandeler(x, y, button, modifiers)
	@window.event
	def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
		mouseDragHandeler(x, y, dx, dy, buttons, modifiers)
	@window.event
	def on_resize(width, height):
		global windowSize
		windowSize = (width, height)
		setPositions()
	@window.event
	def on_mouse_scroll(x, y, scroll_x, scroll_y):
		mouseScrollHandeler(x, y, scroll_x, scroll_y)
	pyglet.app.run()

#draw loop	
def drawFunc():
	global filteredCardList, cardPositions
	for i,card in enumerate(filteredCardList):
		x = cardPositions[i][0]
		y = cardPositions[i][1]
		#cull cards that are off screen
		if (-CARD_HEIGHT <= y) and (y <= windowSize[1]):
			card.image.blit(x, y)

#find the card position in card space of the location the user clicked
def findClickedCardGrid(x,y):
	global cardPositions, windowSize, viewMode, numCardsFiltered
	
	#when the cards are in a grid
	if viewMode == 0:
		#calculate how many cards fit across the screen
		numHorizontalCards = (windowSize[0] - MARGIN) // (CARD_WIDTH + MARGIN)
		
		cardX = (x - MARGIN) // (CARD_WIDTH + MARGIN)
		cardY = (windowSize[1] - y) // (CARD_HEIGHT + MARGIN)
		
		#if the card is outside the range of posible cards return none
		if (cardX + (cardY * numHorizontalCards) > numCardsFiltered) or (cardX < 0) or (cardY < 0):
			return None
		return (cardX, cardY)
	else:
		raise NotImplementedError

#input handeling
def keyboardPressHandeler(symbol, modifiers):
	pass

def keyboardReleaseHandeler(symbol, modifiers):
	global sortMode
	
	if symbol == pyglet.window.key.ENTER:
		commands = input(">> ").lower().strip().split(" ")
		for command in commands:
			if command.startswith("order:"):
				value = command[6:]
				if value in POSSIBLE_SORT_MODES:
					sortMode = value
					filterSortCards()

def mousePressHandeler(x, y, button, modifiers):
	pass

def mouseReleaseHandeler(x, y, button, modifiers):
	pass

def mouseDragHandeler(x, y, dx, dy, button, modifiers):
	pass

def mouseScrollHandeler(x, y, scroll_x, scroll_y):
	global scrollOffset, windowSize, numCardsPerRow, windowSize, numCardsFiltered
	
	scrollOffset += SCROLL_SPEED * scroll_y
	if scrollOffset > 0:
		scrollOffset = 0
	#             (    total number of rows     -        number of rows onscreen            + 1) * (verticle size of a card)
	bottomLimit = ((numCardsFiltered // numCardsPerRow) - (windowSize[1] // (CARD_HEIGHT + MARGIN)) + 1) * (CARD_HEIGHT + MARGIN) * -1
	if scrollOffset < bottomLimit:
		scrollOffset = bottomLimit

	setPositions()

def main():
	loadMetaData()
	loadCards()
	filterSortCards()
	setPositions()
	
	initialisePyglet()

if __name__ == "__main__":
	main()
