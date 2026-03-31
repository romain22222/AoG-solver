from regionHelper import regionSizeHelper, closeRegion
from edges import EdgeState
from constraints.base import Constraint, GridSymbol


class AreaNumberSymbol(GridSymbol):
	def __init__(self, position, size: int):
		super().__init__(position)
		self.size = size

	def propagate(self, state) -> bool:
		parent = state.uf.find(self.position)
		minR, maxR = regionSizeHelper(state, parent)
		if minR > self.size or maxR < self.size:
			return False
		if maxR == self.size or minR == self.size:
			return closeRegion(state, parent, maxR == self.size)
		return True


class AreaNumberConstraint(Constraint):
	def __init__(self, symbols: list[AreaNumberSymbol]):
		self.symbols = symbols

	def propagate(self, state) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state):
				return False
		return True


