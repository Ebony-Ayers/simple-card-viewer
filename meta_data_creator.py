import pyglet
import os
from meta_data_input_handeler import *

CARD_WIDTH = 372
CARD_HEIGHT = 520

#global variables make pyglet much easier to use
#for some reason pygrame needs to frames to draw an image so getnext=2 means get the next image get next=1 means wait a frame and get next=0 means wait for user input
getNext = 2
cardGenerator = None
currentImage = None
metaData = {}

#iterate the generator and catch the errors
def getNextCard():
	global cardGenerator
	try:
		return next(cardGenerator)
	except (RuntimeError, StopIteration):
		return None

#generator for the next image in the folder
def getGenerator():
	cardsFolder = os.path.join(os.getcwd(), "cards/")
	for i,f in enumerate(os.listdir(cardsFolder)):
		if os.path.isfile(os.path.join(cardsFolder, f)):
			yield pyglet.resource.image(os.path.join("cards/", f))
	raise StopIteration

#pyglet poilerplate
def initialisePyglet():
	window = pyglet.window.Window(CARD_WIDTH, CARD_HEIGHT, "Meta data creator")
	@window.event
	def on_draw():
		window.clear()
		drawFunc()
	pyglet.app.run()

#draw loop	
def drawFunc():
	global getNext, currentImage, metaData
	
	#if we are set to get the next card get it and move to the draw step
	if getNext == 2:
		currentImage = getNextCard()
		if currentImage == None:
			return
		currentImage.width = CARD_WIDTH
		currentImage.height = CARD_HEIGHT
		getNext = 1
	
	#draw the current card
	currentImage.blit(0, 0)
	
	#if we are set to get input get input then move to getting the next image
	if getNext == 0:
		createMetaData(metaData)
		getNext = 2
	
	#if we have got the image wait a frame to draw it
	if getNext == 1:
		getNext = 0
	
	#when there are no more images to draw write the meta data to disk
	if currentImage == None:
		outputMetaData(metaData)

def main():
	global cardGenerator
	
	cardGenerator = getGenerator()	
	
	initialisePyglet()

if __name__ == "__main__":
	main()
