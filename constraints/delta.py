from constraints import EdgeSymbol
from constraints.base import SymbolConstraint
from edges import FullEdge
from regionHelper import get_region_shape, joinRegions
from solver import compareSolution, checkOrDie


class DeltaSymbol(EdgeSymbol):
	def __init__(self, edge: FullEdge):
		super().__init__(edge)
		self.text = "δ"

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		if not super().propagate(state):
			return False
		r1, r2 = state.uf.find(self.edge[0][0]), state.uf.find(self.edge[1][0])
		r1Closed, r2Closed = len(state.uf.connectables[r1]) == 0, len(state.uf.connectables[r2]) == 0
		r1Shape, r2Shape = get_region_shape(state, r1), get_region_shape(state, r2)
		if not r1Closed and not r2Closed:
			return True
		if r1Shape == r2Shape:
			if r1Closed and r2Closed:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			if r1Closed:
				if len(state.uf.connectables[r2]) == 1:
					res = joinRegions(state, r2, next(iter(state.uf.connectables[r2])))
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
			else:
				if len(state.uf.connectables[r1]) == 1:
					res = joinRegions(state, r1, next(iter(state.uf.connectables[r1])))
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
		return True


class DeltaConstraint(SymbolConstraint):
	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state, solutionState, matchesSolutionState):
				return False
		return True
