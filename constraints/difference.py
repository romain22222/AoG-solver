from constraints import EdgeSymbol
from constraints.base import SymbolConstraint
from edges import FullEdge
from solver import checkOrDie


class DifferenceSymbol(EdgeSymbol):
	def __init__(self, edge: FullEdge, count: int):
		super().__init__(edge)
		self.count = count
		self.text = count

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		if not super().propagate(state):
			checkOrDie(state, solutionState, matchesSolutionState)
			return False
		r1, r2 = state.uf.find(self.edge[0][0]), state.uf.find(self.edge[1][0])
		r1Closed, r2Closed = len(state.uf.connectables[r1]) == 0, len(state.uf.connectables[r2]) == 0
		r1Size, r2Size = state.uf.size[r1], state.uf.size[r2]
		if r1Closed and r2Closed:
			res = abs(r1Size - r2Size) == self.count
			if not res:
				checkOrDie(state, solutionState, matchesSolutionState)
			return res
		return True


class DifferenceConstraint(SymbolConstraint):
	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state, solutionState, matchesSolutionState):
				return False
		return True
