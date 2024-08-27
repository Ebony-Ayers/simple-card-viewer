import pyglet
import os

CARD_WIDTH = 260
CARD_HEIGHT = 364
MARGIN = 10
#units are pixles per frame
SCROLL_SPEED = 15

#global variables make pyglet much easier to use
numCards = 0
cardImages = []
cardNames = []
cardPositions = []
#enum:
#0 - grid
viewMode = 0
selectedCard = None
windowSize = (1280, 720)
#how many pixles to shift images as a result of scrolling
scrollOffset = 0

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
			cardNames.append(f[:-4])
			numCards += 1

#creeate a list of positions for the cards. The position stored is the bottom left corner.
def setPositions():
	global numCards, cardPositions, windowSize
	cardPositions = [None] * numCards
	x = 0
	y = 0
	maxX = (windowSize[0] - MARGIN) // (CARD_WIDTH + MARGIN)
	for i in range(numCards):
		cardPositions[i] = ((x * (CARD_WIDTH + MARGIN)) + MARGIN, windowSize[1] - ((y+1) * (CARD_HEIGHT + MARGIN)) - scrollOffset)
		x += 1
		if x >= maxX:
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
	global cardImages, cardPositions
	for i,image in enumerate(cardImages):
		x = cardPositions[i][0]
		y = cardPositions[i][1]
		#cull cards that are off screen
		if (-CARD_HEIGHT <= y) and (y <= windowSize[1]):
			image.blit(x, y)

#find the card position in card space of the location the user clicked
def findClickedGardGrid(x,y):
	global cardPositions, windowSize, viewMode, numcards
	
	#when the cards are in a grid
	if viewMode == 0:
		#calculate how many cards fit across the screen
		numHorizontalCards = (windowSize[0] - MARGIN) // (CARD_WIDTH + MARGIN)
		
		cardX = (x - MARGIN) // (CARD_WIDTH + MARGIN)
		cardY = (windowSize[1] - y) // (CARD_HEIGHT + MARGIN)
		
		#if the card is outside the range of posible cards return none
		if (cardX + (cardY * numHorizontalCards) > numCards) or (cardX < 0) or (cardY < 0):
			return None
		return (cardX, cardY)
	else:
		raise NotImplementedError

#input handeling
def mousePressHandeler(x, y, button, modifiers):
	pass
def mouseReleaseHandeler(x, y, button, modifiers):
	pass
def mouseDragHandeler(x, y, dx, dy, button, modifiers):
	pass
def mouseScrollHandeler(x, y, scroll_x, scroll_y):
	global scrollOffset
	scrollOffset += SCROLL_SPEED * scroll_y
	setPositions()

def main():
	loadCards()
	setPositions()
	
	initialisePyglet()

if __name__ == "__main__":
	main()
