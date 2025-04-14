import pyglet
import os
import sys
from meta_data_input_handeler import *

CARD_WIDTH = 372
CARD_HEIGHT = 520
DATA_BASE_FILE_NAME = "cardDB.txt"
CARDS_FOLDER_NAME = "cards/"

#global variables make pyglet much easier to use
#for some reason pygrame needs to frames to draw an image so getnext=2 means get the next image get next=1 means wait a frame and get next=0 means wait for user input
getNext = 2
#generator function to get the next card
cardGenerator = None
currentImage = None
currentCardName = ""
metaData = {}
#command line arguments
shouldSkipExistingCards = False
shouldMofigyExistingCards = False
modifySingleCard = False
modifySingleCardname = ""
propertiesToModify = ["cardType", "subType", "legendary", "cmc", "color", "p/t", "keywords", "abilities", "rarity"]
isDebug = False

#iterate the generator and catch the errors
def getNextCard():
	global cardGenerator
	try:
		return next(cardGenerator)
	except (RuntimeError, StopIteration):
		return (None, "")

#generator for the next image in the folder
def getGenerator():
	cardsFolder = os.path.join(os.getcwd(), CARDS_FOLDER_NAME)
	for i,f in enumerate(os.listdir(cardsFolder)):
		if os.path.isfile(os.path.join(cardsFolder, f)):
			yield (pyglet.resource.image(os.path.join(CARDS_FOLDER_NAME, f)), f)
	raise StopIteration

#pyglet poilerplate
def initialisePyglet():
	global isDebug

	window = pyglet.window.Window(CARD_WIDTH, CARD_HEIGHT, "Meta data creator")
	@window.event
	def on_draw():
		window.clear()
		drawFunc(window)
	
	#closing a pyglet window throws an error message so to avoid confusing exceptions here are supressed
	try:
		pyglet.app.run()
	except Exception as e:
		if isDebug:
			raise e

#draw loop	
def drawFunc(window):
	global getNext, currentImage, currentCardName, metaData, shouldSkipExistingCards, shouldMofigyExistingCards, modifySingleCard, modifySingleCardname, propertiesToModify
	
	if getNext != -1:
		#if we are set to get the next card get it and move to the draw step
		if getNext == 2:
			currentImage, currentCardName = getNextCard()
			if not (modifySingleCard and currentCardName != modifySingleCardname):
				if currentImage != None:
					currentImage.width = CARD_WIDTH
					currentImage.height = CARD_HEIGHT
					getNext = 1
		
		#draw the current card
		if currentImage != None:
			currentImage.blit(0, 0)
		
		#if we are set to get input get input then move to getting the next image
		if getNext == 0:
			createMetaData(metaData, currentCardName, shouldSkipExistingCards, shouldMofigyExistingCards, modifySingleCard, propertiesToModify)
			getNext = 2
		
		#if we have got the image wait a frame to draw it
		if getNext == 1:
			getNext = 0
		
		#when there are no more images to draw write the meta data to disk
		if currentImage == None:
			serialiseMetaData(metaData, DATA_BASE_FILE_NAME)
			#stop the loop from doing anything
			window.close()

def main():
	global cardGenerator, metaData, shouldSkipExistingCards, shouldMofigyExistingCards, modifySingleCard, modifySingleCardname, propertiesToModify, isDebug
	
	#command line arguments
	for arg in sys.argv:
		if arg == "--skip-existing":
			shouldSkipExistingCards = True
			shouldMofigyExistingCards = False
		if arg == "--modify-existing":
			shouldSkipExistingCards = False
			shouldMofigyExistingCards = True
		if arg.startswith("--modify="):
			modifySingleCard = True
			shouldMofigyExistingCards = True
			modifySingleCardname = arg[9:].strip()
		if arg.startswith("--property="):
			properties = arg[11:].strip().split(" ")
			for p in properties:
				if p not in propertiesToModify:
					print(f"Error: property \"{p}\" not valid.")
					return
			propertiesToModify = properties
		if arg == "--debug":
			isDebug = True
	
	#if present read in the existing meta data
	if os.path.isfile(DATA_BASE_FILE_NAME):
		deserialiseMetaData(metaData, DATA_BASE_FILE_NAME)
	
	#if there are cards start the application
	if os.path.isdir(CARDS_FOLDER_NAME):
		cardGenerator = getGenerator()
		initialisePyglet()
	else:
		print("Error: no cards present.")

if __name__ == "__main__":
	main()
