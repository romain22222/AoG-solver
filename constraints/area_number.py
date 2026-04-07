from constraints.base import Constraint, GridSymbol
from regionHelper import regionSizeHelper, closeRegion
from solver import checkOrDie


class AreaNumberSymbol(GridSymbol):
	def __init__(self, position, size: int):
		super().__init__(position)
		self.size = size

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		parent = state.uf.find(self.position)
		minR, maxR = regionSizeHelper(state, parent)
		if minR > self.size or maxR < self.size:
			checkOrDie(matchesSolutionState, state, solutionState)
			return False
		if maxR == self.size or minR == self.size:
			res = closeRegion(state, parent, maxR == self.size)
			if not res:
				checkOrDie(matchesSolutionState, state, solutionState)
			return res
		return True


class AreaNumberConstraint(Constraint):
	def __init__(self, symbols: list[AreaNumberSymbol]):
		self.symbols = symbols

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state, solutionState, matchesSolutionState):
				return False
		return True


