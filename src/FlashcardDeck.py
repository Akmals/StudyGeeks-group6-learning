class FlashcardDeck:
	def __init__(self,name,category,flashcards):
		self.name = name
		self.category = category
		self._flashcards = flashcards
	def getName(self):
		return self.name
	def getCategory(self):
		return self.category
	def getCard(self,index):
		if (index > len(self._flashcards)):
			return "Invalid Index!"
		return self._flashcards[index]
	def getDeckLength(self):
		return len(self._flashcards)
	def addCard(self,flashcard):
		self._flashcards.append(flashcard)
	def removeCard(self,index):
		if (index > len(self._flashcards)):
			return "Invalid Index!"
		del self._flashcards[index]
