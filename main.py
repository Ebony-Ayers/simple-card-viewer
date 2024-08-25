import pyglet
import os

CARD_WIDTH = 260
CARD_HEIGHT = 364
MARGIN = 10

#global variables make pyglet much easier to use
numCards = 0
cardImages = []
cardNameLookup = {}
cardPositions = []

#cache the images for each of the cards
def loadCards():
	global numCards, cardImages, cardNameLookup
	cardsFolder = os.path.join(os.getcwd(), "cards/")
	for i,f in enumerate(os.listdir(cardsFolder)):
		if os.path.isfile(os.path.join(cardsFolder, f)):
			cardImages.append(pyglet.resource.image(os.path.join("cards/", f)))
			#reduce the size to be reasonable
			cardImages[-1].width = CARD_WIDTH
			cardImages[-1].height = CARD_HEIGHT
			cardNameLookup[f[:-4]] = i
			numCards += 1

def setPositions():
	global numCards, cardPositions
	cardPositions = [None] * numCards
	for i in range(numCards):
		cardPositions[i] = (i * (CARD_WIDTH + MARGIN), 0)
	

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
	def on_mouse_press(x, y, button, modifiers):
		mousePressHandeler(x, y, button, modifiers)
	@window.event
	def on_mouse_release(x, y, button, modifiers):
		mouseReleaseHandeler(x, y, button, modifiers)
	@window.event
	def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
		mouseDragHandeler(x, y, dx, dy, buttons, modifiers)
	pyglet.app.run()

#draw loop	
def drawFunc():
	global cardImages, cardPositions
	for i,image in enumerate(cardImages):
		image.blit(cardPositions[i][0], cardPositions[i][1])

#input handeling
def mousePressHandeler(x, y, button, modifiers):
	pass
def mouseReleaseHandeler(x, y, button, modifiers):
	pass
def mouseDragHandeler(x, y, dx, dy, button, modifiers):
	pass

def main():
	loadCards()
	setPositions()
	
	initialisePyglet()

if __name__ == "__main__":
	main()
