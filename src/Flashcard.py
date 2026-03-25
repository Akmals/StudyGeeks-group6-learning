class Flashcard:
	def __init__(self,question,answer):
		self._question = question
		self._answer = answer

	def getQuestion(self):
		return self._question
	def getAnswer(self):
		return self._answer
	def compareAnswer(self,answer):
		return answer.lower().strip() == self._answer.lower().strip()
