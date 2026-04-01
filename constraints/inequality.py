from constraints import EdgeSymbol
from constraints.base import SymbolConstraint
from direction import Direction
from edges import FullEdge
from regionHelper import closeRegion, joinRegions

ORIENTATIONTEXT = {
	Direction.N: "^",
	Direction.S: "v",
	Direction.W: "<",
	Direction.E: ">",
}


class InequalitySymbol(EdgeSymbol):
	def __init__(self, edge: FullEdge, orientation: Direction):
		super().__init__(edge)
		self.orientation = orientation
		self.text = ORIENTATIONTEXT[orientation]
		self.cantWork = not (
			orientation in [Direction.N, Direction.S] if edge[0][1] in [Direction.S, Direction.N] else orientation in [
				Direction.W, Direction.E])
		self.minMax = [self.edge[0][0], self.edge[1][0]]
		if self.orientation == self.edge[1][1]:
			self.minMax[0], self.minMax[1] = self.minMax[1], self.minMax[0]

	def propagate(self, state) -> bool:
		if not self.cantWork:
			return False
		if not super().propagate(state):
			return False
		r1, r2 = state.uf.find(self.minMax[0]), state.uf.find(self.minMax[1])
		r1Closed, r2Closed = len(state.uf.connectables[r1]) == 0, len(state.uf.connectables[r2]) == 0
		r1Size, r2Size = state.uf.size[r1], state.uf.size[r2]
		if r1Closed and r2Closed:
			return r1Size < r2Size
		if r1Closed:
			if len(state.uf.connectables[r2]) == 1:
				if not joinRegions(state, r2, next(iter(state.uf.connectables[r2]))):
					return False
		elif r2Closed:
			if r1Size >= r2Size:
				return False
			if r1Size + 1 == r2Size:
				if not closeRegion(state, r1):
					return False
		return True


class InequalityConstraint(SymbolConstraint):
	def propagate(self, state) -> bool:
		for s in self.symbols:
			if not s.propagate(state):
				return False
		return True
