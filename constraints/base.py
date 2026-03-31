class Constraint:
	def propagate(self, state) -> bool:
		return True


class Symbol:
	def __init__(self):
		pass

	def propagate(self, state) -> bool:
		return True


class GridSymbol(Symbol):
	def __init__(self, position):
		super().__init__()
		self.position = position
